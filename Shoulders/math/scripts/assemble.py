import os
S=os.path.dirname(os.path.abspath(__file__))
OUT=os.environ.get('OUT_DIR',S)
t=open(S+'/template.html').read(); app=open(S+'/app.js').read(); d=open(S+'/data.json').read().replace('</','<\\/')
def page(lang,full,alt=None):
    body=t.replace('__TITLE__','巨人之肩 · On Whose Shoulders' if not alt else ('巨人之肩' if lang=='zh' else 'On Whose Shoulders')).replace('__APP__','window.__LANG__='+repr(lang)+';'+('window.__ALT__='+repr(alt)+';' if alt else '')+'\n'+app).replace('__DATA__',d)
    if not full: return body
    i=body.index('</style>')+8
    desc='OpenAI 722 篇 AI 数学预印本引用了哪些人类数学家：基石地图、各国数学家与菲尔兹奖、阿贝尔奖得主的引文索引。' if lang=='zh' else 'Which human mathematicians do OpenAI’s 722 AI-written math preprints cite? A foundations map, countries, and Fields and Abel laureates.'
    return f'<!doctype html>\n<html lang="{"zh-CN" if lang=="zh" else "en"}">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n<meta name="description" content="{desc}">\n'+body[:i]+'\n</head>\n<body>\n'+body[i:]+'\n</body>\n</html>\n'
open(S+'/shoulders.html','w').write(page('zh',False))
open(OUT+'/index.html','w').write(page('zh',True,'en/'))
os.makedirs(OUT+'/en',exist_ok=True)
open(OUT+'/en/index.html','w').write(page('en',True,'../'))
print('ok',os.path.getsize(OUT+'/index.html')/1e6)
