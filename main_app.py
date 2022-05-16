from __init__ import app, log
import app_config as cfg
from flask import make_response, request, send_from_directory
import requests
import pdfrw
import os


writer = pdfrw.PdfWriter()


def save_doc_to_file(url, text):
    print('WE are in save_doc_to_file')
    if os.path.exists(url):
        os.remove(url)
    with open(url, "wb") as file:
        file.write(text)
    log.info(f"------>SAVE PDF TO FILE: {url}")


def get_pdf(appId, lang):
    url = f'http://{cfg.service_host}:{cfg.service_port}/ipsc/receipt.sv?lang={lang}&appId={appId}'
    success = 0
    try:
        resp = requests.get(url)
        resp_text = resp.content
        resp.close()
        save_doc_to_file(f'{cfg.SPOOL}/{appId}.pdf', resp_text)
        del resp_text
        status = 1
        log.info(f'-----> SEND REQUEST. <  SEND  >. appId: {appId}, lang: {lang}, url: {url}')
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
    for page in pdfrw.PdfReader(ifile).pages:
        newpage = pdfrw.PageMerge()
        newpage.add(page, viewrect=(0, 0, 0.5, 1))
        writer.addpages([newpage.render()])
    writer.write(ofile)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    if cfg.debug_level > 0:
        log.debug(f"file for upload: {cfg.REPORTS_PATH}/{filename}")
    return send_from_directory(cfg.REPORTS_PATH, filename)


# https://notes.gov4c.kz/ipsc/receipt.sv?lang=ru&appId=002224748721
@app.route('/ipsc/receipt.sv', methods=['POST', 'GET'])
def get_request():
    log.info(f"----> SERVICE START.")
    # if request.method == "POST":
    status = 0
    try:
        lang = request.args.get('lang')
        appId = request.args.get('appId')
        log.info(f"+++++ GET: appId: '{appId}', lang: {lang}")
        if appId:
            status, text = get_pdf(appId, lang)
            print(f"-----------> status: {status}, text: {text}")
            if status:
                cut_pdf(f"{cfg.SPOOL}/{appId}.pdf", f"{cfg.SPOOL}/{appId}-2.pdf")
                return send_from_directory(f"{cfg.SPOOL}", f"{appId}-2.pdf")
            else:
                log.error(f"ERROR REQUEST: {appId}")
    except Exception as e:
        log.error(f"GET VALUES: {appId} : {lang}. error: {e}")
    finally:
        if status:
            send_from_directory(f"{appId}-2.pdf")
            return f"<html><h1>Request RECEIPT with appId: {appId} FOUND!</h1></html>"
        else:
            return f"<html><h1>Request RECEIPT with appId: '{appId}' not FOUND</h1></html>"


# https://notes.gov4c.kz/ipsc/receipt.sv?lang=ru&appId=002224748721
@app.route('/')
def root_request():
    return f"<html><h1>Request RECEIPT not found</h1></html>"


if __name__ == "__main__":
    log.info(f"===> Main Receipt started on {cfg.host}:{cfg.port}, work_dir: {cfg.BASE}")
    # get_pdf('002224748721', 'ru')
    app.run(host=cfg.host, port=cfg.port, debug=False)
