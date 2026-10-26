import zipfile, re, sys, os
sys.stdout.reconfigure(encoding='utf-8')
pptx, outdir, slides = sys.argv[1], sys.argv[2], [int(s) for s in sys.argv[3].split(',')]
z = zipfile.ZipFile(pptx)
os.makedirs(outdir, exist_ok=True)
for n in slides:
    xml = z.read(f'ppt/slides/slide{n}.xml').decode('utf8')
    rels = z.read(f'ppt/slides/_rels/slide{n}.xml.rels').decode('utf8')
    relmap = dict(re.findall(r'Id="(rId\d+)"[^>]*Target="\.\./media/([^"]+)"', rels))
    relmap.update({a:b for b,a in re.findall(r'Target="\.\./media/([^"]+)"[^>]*Id="(rId\d+)"', rels)})
    print(f'--- slide {n}')
    for pic in re.findall(r'<p:pic>(.*?)</p:pic>', xml, flags=re.S):
        name = re.search(r'<p:cNvPr[^>]*name="([^"]*)"', pic); descr = re.search(r'descr="([^"]*)"', pic)
        rid = re.search(r'r:embed="(rId\d+)"', pic)
        off = re.search(r'<a:off x="(\d+)" y="(\d+)"', pic); ext = re.search(r'<a:ext cx="(\d+)" cy="(\d+)"', pic)
        media = relmap.get(rid.group(1)) if rid else None
        if media:
            src = z.read('ppt/media/'+media)
            dst = os.path.join(outdir, f's{n}_{media}')
            open(dst,'wb').write(src)
        print(f"{media} | name={name.group(1) if name else ''} | descr={(descr.group(1) if descr else '')[:60]} | x={int(off.group(1))//9525 if off else '?'} y={int(off.group(2))//9525 if off else '?'} w={int(ext.group(1))//9525 if ext else '?'} h={int(ext.group(2))//9525 if ext else '?'}")
