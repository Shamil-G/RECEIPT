from __init__ import app, log
import app_config as cfg
from flask import make_response, request, send_from_directory
import requests
import pdfrw
import os


def save_doc_to_file(url, text):
    if os.path.exists(url):
        os.remove(url)
    with open(url, "wb") as file:
        file.write(text)
    log.info(f"------>SAVED PDF TO FILE: {url}")


def get_pdf(appId, lang):
    url = ''
    if appId[0:3] == '002':
        url = f'http://{cfg.service_host_002}:{cfg.service_port_002}/ipsc/receipt.sv?lang={lang}&appId={appId}'
    elif appId[0:3] == '004':
        url = f'http://{cfg.service_host_004}:{cfg.service_port_004}/ipsc/receipt.sv?lang={lang}&appId={appId}'
    success = 0
    try:
        resp = requests.get(url)
        resp_text = resp.content
        resp.close()
        if resp.status_code == 200:
            save_doc_to_file(f'{cfg.SPOOL}/{appId}.pdf', resp_text)
            success = 1
            log.info(f'----> GET PDF. appId: {appId}, lang: {lang}, url: {url}, {resp.status_code}')
        else:
            log.error(f'----> ERROR GET PDF. appId: {appId}, lang: {lang}, status_code: {resp.status_code}, url: {url}')
        del resp_text
    except requests.exceptions.Timeout as errT:
        log.error(f'ERROR TIMEOUT. SEND RESULT TO ARM GO. num_order: {appId} : {errT}')
    except requests.exceptions.TooManyRedirects as errM:
        log.error(f'ERROR MANY REDIRECT. SEND RESULT TO ARM GO. num_order: {appId} : {errM}')
    except requests.exceptions.ConnectionError as errC:
        log.error(f'ERROR Connection. SEND RESULT TO ARM GO. num_order: {appId} : {errC}')
    except requests.exceptions.RequestException as errE:
        log.error(f'ERROR Exception. SEND RESULT TO ARM GO. num_order: {appId} : {errE}')
    except Exception as ex:
        log.error(f'ERROR Exception. SEND RESULT TO ARM GO. num_order: {appId} : {ex}')
    finally:
        return success


def cut_pdf(ifile: str, ofile: str):
    writer = pdfrw.PdfWriter()
    try:
        for page in pdfrw.PdfReader(ifile).pages:
            newpage = pdfrw.PageMerge()
            newpage.add(page, viewrect=(0, 0, 0.5, 1))
            writer.addpages([newpage.render()])
        writer.write(ofile)
        log.info(f"===> CUT PDF for {ifile} EXECUTED")
        del writer
        return ''
    except pdfrw.errors.PdfParseError as e:
        log.error(f"ERROR CUT PDF: {e}")
        return e



# https://notes.gov4c.kz/ipsc/receipt.sv?lang=ru&appId=002224748721
@app.route('/ipsc/result.sv', methods=['POST', 'GET'])
@app.route('/ipsc/receipt.sv', methods=['POST', 'GET'])
def get_request():
    status = 0
    # if request.method == "POST":
    try:
        lang = request.args.get('lang')
        appId = request.args.get('appId')
        log.info(f"SERVICE REQUESTED: appId: '{appId}', lang: {lang}")
        if appId:
            if not os.path.exists(f'{cfg.SPOOL}/{appId}-2.pdf'):
                status = get_pdf(appId, lang)
            else:
                status = 2
    except Exception as e:
        log.error(f"GET VALUES: {appId} : {lang}. error: {e}")
    finally:
        if status > 0:
            if status == 1:
                mistake_pdf = cut_pdf(f"{cfg.SPOOL}/{appId}.pdf", f"{cfg.SPOOL}/{appId}-2.pdf")
                # os.remove(f"{cfg.SPOOL}/{appId}.pdf")
                if mistake_pdf:
                    return f"<html><h1>Расписка №'{appId}: {mistake_pdf}</h1></html>", 200
            log.info(f"Передаем расписку №{appId}")
            return send_from_directory(f"{cfg.SPOOL}", f"{appId}-2.pdf")
        else:
            return f"<html><h1>Запрошенная расписка №'{appId} не найдена'</h1></html>", 400
    # res = make_response(f'<h2>Service READY.</h2><p>Must be used POST method like this:<p><h3>'
    #                     f'https://notes.gov4c.kz/ipsc/receipt.sv?lang=ru&appId=002228892389</h3')
    # return res, 200

# https://notes.gov4c.kz/ipsc/receipt.sv?lang=ru&appId=002224748721
# http://localhost/ipsc/receipt.sv?lang=ru&appId=002228892389
@app.route('/')
def root_request():
    return f"<html><h1>Request RECEIPT not found</h1></html>"


if __name__ == "__main__":
    log.info(f"===> Main Receipt started on {cfg.host}:{cfg.port}, work_dir: {cfg.BASE}")
    # get_pdf('002224748721', 'ru')
    app.run(host=cfg.host, port=cfg.port, debug=False)
