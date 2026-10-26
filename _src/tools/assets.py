import os
from PIL import Image
W = r"C:\Users\Aden Then\Documents\Aegis-Website"
P = os.path.join(W, "_work", "extract", "profile"); I = os.path.join(W, "_work", "extract", "ipo")
clients = {  # slug: source file (best resolution available)
 "chin-hin": "s19_image59.png", "pavilion-reit": "s18_image62.png", "solarvest": "s19_image74.png",
 "nct-alliance": "s19_image81.png", "signature-international": "s19_image92.png", "seg-international": "s19_image70.png",
 "paragon-globe": "s19_image66.png", "fiamma": "s19_image87.png", "ekovest": "s19_image63.png",
 "xl-holdings": "s19_image61.png", "avangaad": "s19_image82.png", "meta-bright": "s19_image65.png",
 "cab-cakaran": "s19_image71.jpg", "titijaya": "s19_image80.png", "cape-ems": "s19_image73.png",
 "lay-hong": "s19_image86.png", "trc-synergy": "s19_image88.png", "fbg": "s19_image75.jpg",
 "resintech": "s19_image56.jpg", "agmo": "s18_image37.png", "owg": "s19_image52.png",
 "mestron": "s19_image78.jpg", "luster": "s19_image90.png", "g-capital": "s19_image77.png",
 "xin-hwa": "s19_image50.png", "reach-energy": "s19_image102.png", "kinergy": "s19_image68.png",
 "northern-solar": "s19_image91.png", "mag-holdings": "s19_image72.png", "tsa-group": "s18_image58.png",
 "autocount": "s19_image100.png", "bus-cap": "s18_image93.png", "mmcs": "s18_image57.png",
 "ict-zone": "s18_image47.png", "elsa": "s18_image48.png", "hextar-capital": "s19_image69.jpg",
 "sag": "s19_image84.png", "gb-bond": "s18_image76.png",
}
photos = {  # slug: (source, deck) 
 "ir-group-briefing": "s6_image7.png", "ir-boardroom-briefing": "s6_image12.png", "ir-webinar": "s6_image23.png",
 "ir-analyst-briefing": "s6_image27.png", "pr-media-interview": "s8_image14.png", "pr-media-briefing": "s8_image22.png",
 "pr-brand-event": "s8_image25.png", "pr-brand-event-2": "s8_image3.png", "ipo-listing-ceremony": "s11_image19.png",
 "ipo-underwriting-signing": "s11_image28.png", "ipo-prospectus-launch": "s11_image54.png",
 "event-guests": "s13_image15.png", "event-hall": "s13_image22.png", "event-jv-signing": "s13_image30.png",
 "event-underwriting-signing": "s13_image31.png",
}
ipo_photos = {"ipo-prospectus-launch-2": "s9_image23.png", "ipo-press-conference": "s9_image26.png", "ipo-listing-ceremony-2": "s9_image51.png"}
os.makedirs(os.path.join(W,"assets","clients"), exist_ok=True)
low = []
for slug, f in clients.items():
    im = Image.open(os.path.join(P, f)).convert("RGBA")
    if im.width < 220 or im.height < 70: low.append((slug, im.size))
    if im.width > 600: im.thumbnail((600, 600))
    im.save(os.path.join(W,"assets","clients",slug+".png"), optimize=True)
def photo(src, slug):
    im = Image.open(src).convert("RGB"); im.thumbnail((1600,1600))
    im.save(os.path.join(W,"assets","photos",slug+".jpg"), quality=82, optimize=True, progressive=True)
for slug,f in photos.items(): photo(os.path.join(P,f), slug)
for slug,f in ipo_photos.items(): photo(os.path.join(I,f), slug)
Image.open(os.path.join(P,"s20_image121.png")).save(os.path.join(W,"assets","network","investment-community.png"), optimize=True)
Image.open(os.path.join(P,"s20_image118.png")).save(os.path.join(W,"assets","network","media.png"), optimize=True)
print("low-res logos:", low)
