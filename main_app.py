from __init__ import app, log
import app_config as cfg
from flask import make_response, request, send_from_directory
import requests
import pdfrw


writer = pdfrw.PdfWriter()


def get_pdf(appId, lang):
    url = f'http://{cfg.service_host}:{cfg.service_port}/ipsc/receipt.sv?lang={lang}&appId={appId}'
    success = 0
    try:
        log.info(f'-----> SEND REQUEST. <  SEND  >. appId: {appId}, lang: {lang}, url: {url}')
        resp = requests.post(url)
        resp_json = resp.json()
        send_status = resp_json["status"]
        resp.close()
        success = 1
        log.info(f'-----> SEND RESULT TO ARM GO. <RESPONSE>. NUM_ORDER: {appId}, response: {resp_json}')
    except requests.exceptions.Timeout as errT:
        log.error(f'TIMEOUT ERROR. SEND RESULT TO ARM GO. num_order: {appId} : {errT}')
    except requests.exceptions.TooManyRedirects as errM:
        log.error(f'ERROR MANY REDIRECT. SEND RESULT TO ARM GO. num_order: {appId} : {errM}')
    except requests.exceptions.ConnectionError as errC:
        log.error(f'ERROR CONNECTION. SEND RESULT TO ARM GO. num_order: {appId} : {errC}')
    except requests.exceptions.RequestException as errE:
        log.error(f'REQUEST ERROR. SEND RESULT TO ARM GO. num_order: {appId} : {errE}')
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
        log.info(f"GET VALUES: {appId} : {lang}")
        if appId:
            status = get_pdf(appId, lang)
            if status:
                log.error(f"GET REQUEST, RECEIPT FOUND. appId: {appId}")
                cut_pdf(f"{appId}.pdf", f"{appId}-2.pdf")
            else:
                log.error(f"ERROR REQUEST: {appId}")
    except Exception as e:
        log.info(f"GET VALUES: {appId} : {lang}")
    finally:
        if status:
            send_from_directory(f"{appId}-2.pdf")
            return f"<html><h1>Request RECEIPT {appId} FOUND!</h1></html>"
        else:
            return f"<html><h1>Request RECEIPT {appId} not FOUND</h1></html>"


# https://notes.gov4c.kz/ipsc/receipt.sv?lang=ru&appId=002224748721
@app.route('/')
def root_request():
    return f"<html><h1>Request RECEIPT not found</h1></html>"


if __name__ == "__main__":
    log.info(f"===> Main Receipt started on {cfg.host}:{cfg.port}, work_dir: {cfg.BASE}")
    app.run(host=cfg.host, port=cfg.port, debug=False)
