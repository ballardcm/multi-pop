#!/usr/bin/env python3
"""Relay this repository's GitHub release over a localhost-only SSH tunnel.

Used for private testing and handhelds without Internet access. Authenticate gh on
this computer; no GitHub credential is returned to the handheld.
"""
import argparse, http.server, json, pathlib, re, shutil, subprocess, tempfile, threading
REPO='ballardcm/multi-pop-rgds'
class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path=='/release':
                result=json.loads(subprocess.check_output(['gh','api',f'repos/{REPO}/releases/latest'],stderr=subprocess.PIPE))
                assets=[]
                with self.server.guard:
                    for a in result.get('assets',[]):
                        if a['name']=='SHA256SUMS' or re.fullmatch(r'multi-pop-rgds-rocknix-[0-9]+\.zip',a['name']):
                            self.server.allowed.add(a['id'])
                            assets.append({'name':a['name'],'browser_download_url':f'http://127.0.0.1:{self.server.server_port}/asset/{a["id"]}'})
                data=json.dumps({'tag_name':result['tag_name'],'assets':assets}).encode()
                self.send_response(200);self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data)
            elif re.fullmatch(r'/asset/[0-9]+',self.path):
                asset_id=int(self.path.rsplit('/',1)[1])
                with self.server.guard:
                    if asset_id not in self.server.allowed:self.send_error(404);return
                    path=self.server.cache/str(asset_id)
                    if not path.exists():
                        tmp=path.with_suffix('.tmp')
                        with tmp.open('wb') as out:
                            subprocess.run(['gh','api',f'repos/{REPO}/releases/assets/{asset_id}','-H','Accept: application/octet-stream'],stdout=out,stderr=subprocess.PIPE,check=True)
                        tmp.replace(path)
                self.send_response(200);self.send_header('Content-Length',str(path.stat().st_size));self.end_headers()
                with path.open('rb') as source:shutil.copyfileobj(source,self.wfile)
            else:self.send_error(404)
        except (subprocess.CalledProcessError,ValueError,OSError):
            self.send_error(502,'GitHub release unavailable; check gh authentication and connectivity on the host.')
    def log_message(self,fmt,*args):print(fmt%args,flush=True)
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--port',type=int,default=18765);args=parser.parse_args()
    with tempfile.TemporaryDirectory(prefix='multi-pop-relay-') as tmp:
        server=http.server.ThreadingHTTPServer(('127.0.0.1',args.port),Handler)
        server.cache=pathlib.Path(tmp);server.allowed=set();server.guard=threading.Lock()
        print(f'Relay for {REPO} listening only on 127.0.0.1:{args.port}',flush=True)
        server.serve_forever()
if __name__=='__main__':main()
