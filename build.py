#!/usr/bin/env python3
"""Static site builder for keefa.app.

Run:  python3 build.py
Writes real HTML per language (/ and /ar/), hub, one page per app, sitemap.xml,
robots.txt, llms.txt, 404.html, CNAME and og images. Legal pages (privacy, terms,
support, reset) are hand-written and left alone.

Add an app: add an entry to APPS (and its icon in assets/), run the builder.
Flip an app to live: set status="live" and store_url.
"""
import html, json, re, datetime, pathlib

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / "src"
DOMAIN = "https://keefa.app"
TODAY = datetime.date.today().isoformat()
INDEXNOW_KEY = "63a5c8f3138c4f038b9403a916e2fdee"  # public by design: proves site ownership to IndexNow
IOS = ROOT.parent / "ios" / "apps"

CSS = (SRC / "style.css").read_text(encoding="utf-8")
KEEFA_MAIN = (SRC / "keefa_main.html").read_text(encoding="utf-8")
KEEFA_STR = json.loads((SRC / "keefa_strings.json").read_text(encoding="utf-8"))

LANGS = {
    "en": {"prefix": "", "dir": "ltr", "locale": "en_US", "name": "English", "label": "EN"},
    "ar": {"prefix": "/ar", "dir": "rtl", "locale": "ar_AR", "name": "العربية", "label": "عربي"},
}

# ------------------------------------------------------------------ apps
APPS = [
    dict(slug="keefa", name={"en": "Keefa", "ar": "كيفا"}, folder="wazna", accent="#10B981",
         icon="assets/icon.png", status="soon", store_url="", apple_id="6833574449",
         category="HealthApplication", home="/", legal="https://keefa.app/privacy.html",
         terms="https://keefa.app/terms.html", support="https://keefa.app/support.html",
         sub={"en": "Food scanner, macros, fasting", "ar": "صيام متقطع وبروتين ودايت"},
         promo={"en": "Snap a meal, get calories and macros in seconds. Built for kabsa, mandi, tagine and home cooking, with a fasting timer and suhoor and iftar times.",
                "ar": "صوّر وجبتك واعرف السعرات والماكروز في ثوانٍ. مصمم للكبسة والمندي والأكل البيتي، مع مؤقت صيام ومواعيد السحور والإفطار."}),
    dict(slug="currencyx", name={"en": "CurrencyX", "ar": "CurrencyX"}, folder="currency-x", accent="#3B82F6",
         icon="assets/currencyx.png", status="live", store_url="https://apps.apple.com/app/id6760399044", apple_id="6760399044",
         category="FinanceApplication", home="/currencyx/",
         legal="https://mouloudoujderou-star.github.io/currencyx/privacy/",
         terms="https://mouloudoujderou-star.github.io/currencyx/terms/",
         support="https://mouloudoujderou-star.github.io/currencyx/support/"),
    dict(slug="wayfare", name={"en": "Wayfare", "ar": "Wayfare"}, folder="wayfare", accent="#F59E0B",
         icon="assets/wayfare.png", status="soon", store_url="", apple_id="6831649328",
         category="TravelApplication", home="/wayfare/",
         legal="https://mouloudoujderou-star.github.io/wayfare/privacy/",
         terms="https://mouloudoujderou-star.github.io/wayfare/terms/",
         support="https://mouloudoujderou-star.github.io/wayfare/support/"),
]

G = {  # generic UI strings
    "en": dict(
        apps="Apps", home_title="Apps that make everyday life simpler",
        hub_title="Our apps: Keefa, CurrencyX and Wayfare",
        hub_desc="iPhone apps for food, money and travel: Keefa calorie and macro tracker, CurrencyX currency converter and Wayfare AI travel planner.",
        hub_h1="Useful apps for food, money and travel", hub_sub="Small, honest iPhone apps built for real life in the Gulf, North Africa and beyond. Each one does one job well.",
        live="Available now", soon="Coming soon", learn="Learn more", get="Download on the App Store", soon_btn="Coming soon on the App Store",
        next_h="The next app is on its way", next_p="We keep building. Check back here, every new app gets its own page.",
        features="What you get", pricing="Pricing", faq="Questions, answered", other="More apps",
        privacy="Privacy Policy", terms="Terms of Service", support="Support", breadcrumb_home="Home",
        q_free="Is it free?", q_lang="Which languages does it support?", q_when="Where can I get it?",
        a_live="Download it from the App Store for iPhone.", a_soon="It is coming soon to the App Store for iPhone. Check back on this page for the link.",
        foot_tag="Apps for food, money and travel", disclaimer_store="App Store is a trademark of Apple Inc.",
        site_name="keefa.app", lang_switch="العربية", skip="Skip to content", legal_note="Legal pages are in English.",
    ),
    "ar": dict(
        apps="التطبيقات", home_title="تطبيقات تسهّل حياتك اليومية",
        hub_title="تطبيقاتنا: كيفا وCurrencyX وWayfare",
        hub_desc="تطبيقات آيفون للأكل والمال والسفر: كيفا لحساب السعرات والماكروز، وCurrencyX لتحويل العملات، وWayfare مخطط الرحلات الذكي.",
        hub_h1="تطبيقات مفيدة للأكل والمال والسفر", hub_sub="تطبيقات آيفون صغيرة وصريحة لحياتك الحقيقية في الخليج وشمال أفريقيا وغيرها. كل تطبيق يتقن مهمة واحدة.",
        live="متوفر الآن", soon="قريباً", learn="اعرف أكثر", get="حمّل من App Store", soon_btn="قريباً على App Store",
        next_h="التطبيق القادم في الطريق", next_p="نواصل البناء. تابعنا هنا، وكل تطبيق جديد له صفحته.",
        features="وش تحصل عليه", pricing="الأسعار", faq="أسئلة وأجوبة", other="تطبيقات أخرى",
        privacy="سياسة الخصوصية", terms="شروط الاستخدام", support="الدعم", breadcrumb_home="الرئيسية",
        q_free="هل هو مجاني؟", q_lang="وش اللغات المدعومة؟", q_when="من وين أحمّله؟",
        a_live="حمّله من App Store للآيفون.", a_soon="قريباً على App Store للآيفون. تابع هذه الصفحة لرابط التحميل.",
        foot_tag="تطبيقات للأكل والمال والسفر", disclaimer_store="App Store علامة تجارية لشركة Apple Inc.",
        site_name="keefa.app", lang_switch="English", skip="انتقل للمحتوى", legal_note="الصفحات القانونية بالإنجليزية.",
    ),
}

# ------------------------------------------------------------------ helpers
esc = html.escape


def url(lang, path):
    """Absolute path for a language, path like '/' or '/apps/'."""
    return LANGS[lang]["prefix"] + path


def abs_url(lang, path):
    return DOMAIN + url(lang, path)


def out_file(lang, path):
    p = ROOT / (LANGS[lang]["prefix"].lstrip("/") + path).strip("/")
    p.mkdir(parents=True, exist_ok=True)
    return p / "index.html"


def other(lang):
    return "ar" if lang == "en" else "en"


def store_data(app, lang):
    """Pull store copy from the app's store.config.json (kept in sync with the App Store)."""
    cfg = json.loads((IOS / app["folder"] / "store.config.json").read_text(encoding="utf-8"))["apple"]["info"]
    return cfg["en-US" if lang == "en" else "ar-SA"]


def parse_desc(desc):
    paras = [p.strip() for p in desc.split("\n\n") if p.strip()]
    bullets = [l.lstrip("• ").strip() for l in paras[2].split("\n") if l.strip().startswith("•")]
    return dict(tagline=paras[0], intro=paras[1], bullets=bullets, price=paras[3],
                fine=paras[4], note=paras[-2] if len(paras) > 6 else "")


def head(lang, path, title, desc, og_image, extra_ld, apple_id=None, other_path=None):
    L = LANGS[lang]
    o = other(lang)
    canon = abs_url(lang, path)
    ld = json.dumps({"@context": "https://schema.org", "@graph": extra_ld}, ensure_ascii=False)
    banner = f'<meta name="apple-itunes-app" content="app-id={apple_id}">\n' if apple_id else ""
    return f"""<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<meta name="robots" content="index,follow,max-image-preview:large,max-snippet:-1,max-video-preview:-1">
<meta name="theme-color" content="#090A0F">
<link rel="canonical" href="{canon}">
<link rel="alternate" hreflang="{lang}" href="{canon}">
<link rel="alternate" hreflang="{o}" href="{abs_url(o, other_path or path)}">
<link rel="alternate" hreflang="x-default" href="{abs_url('en', other_path or path) if lang == 'ar' else canon}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="keefa.app">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{DOMAIN}/{og_image}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="{L['locale']}">
<meta property="og:locale:alternate" content="{LANGS[o]['locale']}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(title)}">
<meta name="twitter:description" content="{esc(desc)}">
<meta name="twitter:image" content="{DOMAIN}/{og_image}">
{banner}<link rel="icon" href="/assets/favicon.png" type="image/png">
<link rel="apple-touch-icon" href="/assets/icon.png">
<style>
{CSS}
</style>
<script type="application/ld+json">{ld}</script>"""


def header(lang, path, nav_extra, brand_html, other_path=None):
    g = G[lang]
    o = other(lang)
    nav = "".join(f'<a href="{href}">{esc(label)}</a>' for href, label in nav_extra)
    nav += f'<a href="{url(lang, "/apps/")}">{esc(g["apps"])}</a>'
    switch = (
        f'<div class="lang" role="group" aria-label="Language">'
        f'<a href="{url("en", other_path or path)}" hreflang="en" lang="en" aria-current="{"true" if lang == "en" else "false"}">EN</a>'
        f'<a href="{url("ar", other_path or path)}" hreflang="ar" lang="ar" aria-current="{"true" if lang == "ar" else "false"}">عربي</a></div>'
    )
    return f"""<a class="skip" href="#main">{esc(g['skip'])}</a>
<header><div class="wrap bar">{brand_html}<nav class="links" aria-label="Main">{nav}</nav>{switch}</div></header>"""


def footer(lang):
    g = G[lang]
    apps = "".join(f'<a href="{url(lang, a["home"]) if a["slug"] != "keefa" else url(lang, "/")}">{esc(a["name"][lang])}</a>' for a in APPS)
    return f"""<footer><div class="wrap">
<div class="cols"><div><strong style="color:var(--ink)">keefa.app</strong> &middot; {esc(g['foot_tag'])}</div>
<nav aria-label="Apps">{apps}<a href="{url(lang, '/apps/')}">{esc(g['apps'])}</a></nav>
<nav aria-label="Legal"><a href="/privacy.html">{esc(g['privacy'])}</a><a href="/terms.html">{esc(g['terms'])}</a><a href="/support.html">{esc(g['support'])}</a></nav></div>
<p class="disc">{esc(g['disclaimer_store'])} {esc(g['legal_note']) if lang == 'ar' else ''}</p>
</div></footer>"""


REVEAL_JS = """<script>
(function(){var els=document.querySelectorAll('.reveal');
if('IntersectionObserver' in window){var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}});},{threshold:.12});els.forEach(function(el){io.observe(el);});}
else{els.forEach(function(el){el.classList.add('in');});}})();
</script>"""


def page(lang, path, head_html, hdr, main, ftr):
    L = LANGS[lang]
    return f"""<!doctype html>
<html lang="{lang}" dir="{L['dir']}">
<head>
{head_html}
</head>
<body>
<div class="glow"></div>
{hdr}
<main id="main">
{main}
</main>
{ftr}
{REVEAL_JS}
</body>
</html>
"""


def write(lang, path, content):
    f = out_file(lang, path)
    f.write_text(content, encoding="utf-8")
    return f


SITEMAP = []  # (path)


def brand_app(lang, app):
    return (f'<a class="brand" href="{url(lang, app["home"] if app["slug"] != "keefa" else "/")}">'
            f'<img src="/{app["icon"]}" alt="" width="34" height="34"><span>{esc(app["name"][lang])}</span></a>')


BRAND_SITE = lambda lang: f'<a class="brand" href="{url(lang, "/")}"><span class="dot"></span><span>keefa.app</span></a>'


def store_button(lang, app, label_key=None):
    g = G[lang]
    apple = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M16.4 12.6c0-2.3 1.9-3.4 2-3.5-1.1-1.6-2.8-1.8-3.4-1.8-1.4-.1-2.8.9-3.5.9-.7 0-1.8-.8-3-.8-1.5 0-3 .9-3.8 2.3-1.6 2.8-.4 7 1.2 9.3.8 1.1 1.7 2.4 2.9 2.3 1.2 0 1.6-.7 3-.7s1.8.7 3 .7c1.3 0 2.1-1.1 2.8-2.3.9-1.3 1.3-2.5 1.3-2.6-.1 0-2.5-1-2.5-3.8zM14.2 5.8c.6-.8 1.1-1.9.9-3-.9 0-2.1.6-2.7 1.4-.6.7-1.1 1.8-1 2.9 1.1.1 2.1-.5 2.8-1.3z"/></svg>'
    if app["status"] == "live" and app["store_url"]:
        return f'<a class="store" href="{app["store_url"]}" rel="noopener">{apple}<span><small>{esc(g["get"].split(" ")[0])}</small><b>App Store</b></span></a>'
    return f'<span class="store" aria-label="{esc(g["soon_btn"])}">{apple}<span><small>{esc(g["soon_btn"].replace(" App Store", ""))}</small><b>App Store</b></span></span>'


# ------------------------------------------------------------------ Keefa page
def build_keefa(lang):
    S = KEEFA_STR[lang]
    g = G[lang]
    app = APPS[0]
    main = KEEFA_MAIN

    def repl(m):
        key = m.group(3)
        if key in S:
            return m.group(1) + esc(S[key]).replace("&#x27;", "'") + m.group(5)
        return m.group(0)

    main = re.sub(r'(<(\w+)[^>]*data-i18n="(\w+)"[^>]*>)(.*?)(</\2>)', lambda m: repl(m) if False else
                  (m.group(1) + (esc(S[m.group(3)]).replace("&#x27;", "'") if m.group(3) in S else m.group(4)) + m.group(5)),
                  main, flags=re.S)
    main = re.sub(r'\sdata-i18n="\w+"', "", main)
    main = main.replace('src="assets/icon.png"', 'src="/assets/icon.png"')
    main = main.replace('href="#how"', 'href="#how"')

    title = {"en": "Keefa: Calorie Counter, Food Scanner & Fasting Timer for iPhone",
             "ar": "كيفا: عداد السعرات الحرارية وماسح الأكل ومؤقت الصيام للآيفون"}[lang]
    desc = app["promo"][lang]
    faq_keys = [("q1", "a1"), ("q2", "a2"), ("q3", "a3"), ("q4", "a4"), ("q5", "a5"), ("q6", "a6")]
    ld = [
        {"@type": "WebSite", "@id": DOMAIN + "/#site", "url": DOMAIN + "/", "name": "keefa.app", "inLanguage": ["en", "ar"]},
        {"@type": "MobileApplication", "@id": abs_url(lang, "/") + "#app", "name": "Keefa", "alternateName": ["Keefa: Calorie Counter", "كيفا"],
         "operatingSystem": "iOS", "applicationCategory": "HealthApplication", "description": desc,
         "inLanguage": ["en", "ar", "fr"], "image": DOMAIN + "/assets/icon.png", "url": abs_url(lang, "/"),
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
         "availableOnDevice": "iPhone", "keywords": "calorie counter, macro tracker, food scanner, intermittent fasting, Ramadan, suhoor, iftar"},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": S[q], "acceptedAnswer": {"@type": "Answer", "text": S[a]}} for q, a in faq_keys]},
    ]
    hd = head(lang, "/", title, desc, "assets/og-keefa.png", ld, apple_id=app["apple_id"])
    nav = [("#how", S["nav_how"]), ("#fasting", S["nav_fast"]), ("#pricing", S["nav_price"]), ("#faq", S["nav_faq"])]
    hdr = header(lang, "/", nav, brand_app(lang, app))
    write(lang, "/", page(lang, "/", hd, hdr, main, footer(lang)))
    SITEMAP.append("/")
    # Keefa "other apps" strip is on the hub; keep the landing focused.


# ------------------------------------------------------------------ hub
def build_hub(lang):
    g = G[lang]
    cards = []
    for a in APPS:
        if a["slug"] == "keefa":
            sub, promo = a["sub"][lang], a["promo"][lang]
        else:
            d = store_data(a, lang)
            sub, promo = d["subtitle"], d["promoText"]
        href = url(lang, "/") if a["slug"] == "keefa" else url(lang, a["home"])
        st = "live" if a["status"] == "live" else "soon"
        cards.append(f"""<a class="appcard acc reveal" style="--accent:{a['accent']}" href="{href}">
<img src="/{a['icon']}" alt="{esc(a['name'][lang])} icon" width="68" height="68" loading="lazy">
<span class="status {st}">{esc(g[st])}</span>
<h2>{esc(a['name'][lang])}</h2><p class="st">{esc(sub)}</p><p>{esc(promo)}</p>
<span class="go">{esc(g['learn'])} &rarr;</span></a>""")
    cards.append(f"""<div class="appcard reveal" style="--accent:#8B5CF6;border-style:dashed"><h2>?</h2><p class="st">{esc(g['next_h'])}</p><p>{esc(g['next_p'])}</p></div>""")
    main = f"""<div class="page-head"><div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="{url(lang, '/')}">{esc(g['breadcrumb_home'])}</a> / {esc(g['apps'])}</nav>
<h1>{esc(g['hub_h1'])}</h1><p class="lead">{esc(g['hub_sub'])}</p>
<div class="apps">{''.join(cards)}</div></div></div>"""
    ld = [
        {"@type": "WebSite", "@id": DOMAIN + "/#site", "url": DOMAIN + "/", "name": "keefa.app", "inLanguage": ["en", "ar"]},
        {"@type": "CollectionPage", "name": g["hub_title"], "url": abs_url(lang, "/apps/"), "description": g["hub_desc"],
         "mainEntity": {"@type": "ItemList", "itemListElement": [
             {"@type": "ListItem", "position": i + 1, "url": abs_url(lang, "/" if a["slug"] == "keefa" else a["home"]), "name": a["name"][lang]}
             for i, a in enumerate(APPS)]}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": g["breadcrumb_home"], "item": abs_url(lang, "/")},
            {"@type": "ListItem", "position": 2, "name": g["apps"], "item": abs_url(lang, "/apps/")}]},
    ]
    hd = head(lang, "/apps/", g["hub_title"], g["hub_desc"], "assets/og-keefa.png", ld)
    write(lang, "/apps/", page(lang, "/apps/", hd, header(lang, "/apps/", [], BRAND_SITE(lang)), main, footer(lang)))
    SITEMAP.append("/apps/")


# ------------------------------------------------------------------ generic app page
def build_app(lang, app):
    g = G[lang]
    d = store_data(app, lang)
    p = parse_desc(d["description"])
    name = app["name"][lang]
    path = app["home"]
    feats = []
    for b in p["bullets"]:
        if ":" in b[:60] or "：" in b[:60]:
            title = b.split(":", 1)[0].strip()
            rest = b.split(":", 1)[1].strip()
            rest = rest[:1].upper() + rest[1:]
        else:
            title, rest = b, ""
        feats.append(f'<div class="card reveal"><h3>{esc(title)}</h3>{"<p>" + esc(rest) + "</p>" if rest else ""}</div>')
    lang_bullet = next((b for b in p["bullets"] if re.search(r"12|١٢", b)), "")
    faq = [(g["q_free"], p["price"]), (g["q_when"], g["a_live"] if app["status"] == "live" else g["a_soon"])]
    if lang_bullet:
        faq.insert(1, (g["q_lang"], lang_bullet))
    faq_html = "".join(f"<details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>" for q, a in faq)
    others = "".join(
        f'<a class="appcard acc" style="--accent:{o["accent"]}" href="{url(lang, "/" if o["slug"] == "keefa" else o["home"])}"><img src="/{o["icon"]}" alt="" width="52" height="52" loading="lazy" style="width:52px;height:52px;border-radius:13px"><h3>{esc(o["name"][lang])}</h3></a>'
        for o in APPS if o["slug"] != app["slug"])
    st = "live" if app["status"] == "live" else "soon"
    main = f"""<div class="page-head acc" style="--accent:{app['accent']}"><div class="wrap">
<nav class="crumbs" aria-label="Breadcrumb"><a href="{url(lang, '/')}">{esc(g['breadcrumb_home'])}</a> / <a href="{url(lang, '/apps/')}">{esc(g['apps'])}</a> / {esc(name)}</nav>
<div class="apphero" style="margin-top:22px"><img src="/{app['icon']}" alt="{esc(name)} app icon" width="132" height="132" fetchpriority="high">
<div><span class="status {st}">{esc(g[st])}</span><h1>{esc(d['title'])}</h1><p class="lead" style="margin-bottom:18px">{esc(p['tagline'])}</p>
<div class="cta">{store_button(lang, app)}</div></div></div>
<p class="sub" style="margin-top:34px;max-width:46em">{esc(p['intro'])}</p></div></div>
<section class="acc" style="--accent:{app['accent']};padding-top:30px"><div class="wrap">
<h2>{esc(g['features'])}</h2><div class="feat">{''.join(feats)}</div></div></section>
<section class="alt acc" style="--accent:{app['accent']}"><div class="wrap">
<h2>{esc(g['pricing'])}</h2><p class="sub">{esc(p['price'])}</p><p class="fine">{esc(p['fine'])}</p>
{f'<p class="fine">{esc(p["note"])}</p>' if p['note'] else ''}</div></section>
<section><div class="wrap"><h2>{esc(g['faq'])}</h2><div class="faq">{faq_html}</div>
<div class="links-row acc" style="--accent:{app['accent']}"><a href="{app['legal']}" rel="noopener">{esc(g['privacy'])}</a><a href="{app['terms']}" rel="noopener">{esc(g['terms'])}</a><a href="{app['support']}" rel="noopener">{esc(g['support'])}</a></div>
<h2 style="margin-top:56px;font-size:24px">{esc(g['other'])}</h2><div class="apps" style="grid-template-columns:repeat(auto-fit,minmax(200px,1fr))">{others}</div></div></section>"""
    ld = [
        {"@type": "WebSite", "@id": DOMAIN + "/#site", "url": DOMAIN + "/", "name": "keefa.app", "inLanguage": ["en", "ar"]},
        {"@type": "MobileApplication", "name": d["title"], "alternateName": name, "operatingSystem": "iOS",
         "applicationCategory": app["category"], "description": p["tagline"] + " " + p["intro"], "image": f"{DOMAIN}/{app['icon']}",
         "url": abs_url(lang, path), "inLanguage": lang, "availableOnDevice": "iPhone",
         "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"}, **({"installUrl": app["store_url"]} if app["status"] == "live" else {})},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": g["breadcrumb_home"], "item": abs_url(lang, "/")},
            {"@type": "ListItem", "position": 2, "name": g["apps"], "item": abs_url(lang, "/apps/")},
            {"@type": "ListItem", "position": 3, "name": name, "item": abs_url(lang, path)}]},
    ]
    title = f"{d['title']} | {d['subtitle']}"
    desc = d["promoText"]
    og = f"assets/og-{app['slug']}.png"
    hd = head(lang, path, title, desc, og, ld, apple_id=app["apple_id"])
    write(lang, path, page(lang, path, hd, header(lang, path, [], brand_app(lang, app)), main, footer(lang)))
    SITEMAP.append(path)


# ------------------------------------------------------------------ files
def build_files():
    urls = []
    for path in SITEMAP:
        alts = "".join(
            f'<xhtml:link rel="alternate" hreflang="{l}" href="{abs_url(l, path)}"/>' for l in LANGS)
        alts += f'<xhtml:link rel="alternate" hreflang="x-default" href="{abs_url("en", path)}"/>'
        for l in LANGS:
            urls.append(f"<url><loc>{abs_url(l, path)}</loc><lastmod>{TODAY}</lastmod>{alts}</url>")
    legal = "".join(f"<url><loc>{DOMAIN}/{n}.html</loc><lastmod>{TODAY}</lastmod></url>" for n in ("privacy", "terms", "support"))
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(urls) + "\n" + legal + "\n</urlset>\n", encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\nDisallow: /reset.html\n\n"
        "# AI and answer-engine crawlers are welcome to read the public pages\n"
        "User-agent: GPTBot\nAllow: /\nUser-agent: ClaudeBot\nAllow: /\nUser-agent: PerplexityBot\nAllow: /\nUser-agent: Google-Extended\nAllow: /\n\n"
        f"Sitemap: {DOMAIN}/sitemap.xml\n", encoding="utf-8")
    lines = ["# keefa.app", "",
             "> iPhone apps for food, money and travel, built for everyday life in the Gulf, North Africa and beyond. English and Arabic.", "",
             "## Apps", ""]
    for a in APPS:
        if a["slug"] == "keefa":
            lines.append(f"- [Keefa]({DOMAIN}/): {a['promo']['en']} ({a['status']})")
        else:
            d = store_data(a, "en")
            lines.append(f"- [{d['title']}]({DOMAIN}{a['home']}): {d['promoText']} ({a['status']})")
    lines += ["", "## Arabic pages", ""]
    lines += [f"- [{a['name']['ar']}]({DOMAIN}/ar{'/' if a['slug'] == 'keefa' else a['home']})" for a in APPS]
    lines += ["", "## Legal", "", f"- [Privacy Policy]({DOMAIN}/privacy.html)", f"- [Terms of Service]({DOMAIN}/terms.html)", f"- [Support]({DOMAIN}/support.html)", "",
              "## Facts", "", "- Keefa is not a medical device. Calorie and macro numbers are estimates.",
              "- CurrencyX rates are mid-market rates from public sources and may be delayed. Not financial advice.",
              "- Wayfare opening hours and prices are estimates: check before you go.", ""]
    (ROOT / "llms.txt").write_text("\n".join(lines), encoding="utf-8")
    (ROOT / "CNAME").write_text("keefa.app\n", encoding="utf-8")
    (ROOT / f"{INDEXNOW_KEY}.txt").write_text(INDEXNOW_KEY, encoding="utf-8")
    nf = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="robots" content="noindex"><title>Page not found | keefa.app</title>
<style>body{{margin:0;background:#090A0F;color:#F3F5FA;font:18px/1.6 -apple-system,Segoe UI,Roboto,sans-serif;display:grid;place-items:center;min-height:100vh;text-align:center;padding:20px}}a{{color:#10B981;font-weight:700}}h1{{font-size:56px;margin:0}}</style></head>
<body><div><h1>404</h1><p>That page does not exist.</p><p><a href="/">Home</a> &middot; <a href="/apps/">Apps</a> &middot; <a href="/ar/">العربية</a></p></div></body></html>
"""
    (ROOT / "404.html").write_text(nf, encoding="utf-8")


def build_og():
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return
    bold = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    reg = "/System/Library/Fonts/Helvetica.ttc"
    taglines = {"keefa": ("Keefa", "Snap your meal. See calories and macros."),
                "currencyx": ("CurrencyX", "Your money abroad, clear in one second."),
                "wayfare": ("Wayfare", "Plan any city day by day.")}
    for a in APPS:
        title, tag = taglines[a["slug"]]
        W, H = 1200, 630
        im = Image.new("RGB", (W, H), "#090A0F")
        glow = Image.new("RGB", (W, H), a["accent"])
        mask = Image.new("L", (W, H), 0)
        dm = ImageDraw.Draw(mask)
        dm.ellipse((650, -150, 1350, 500), fill=90)
        from PIL import ImageFilter
        mask = mask.filter(ImageFilter.GaussianBlur(120))
        im.paste(glow, (0, 0), mask)
        icon = Image.open(ROOT / a["icon"]).convert("RGBA").resize((300, 300))
        r = Image.new("L", (300, 300), 0)
        ImageDraw.Draw(r).rounded_rectangle((0, 0, 299, 299), 70, fill=255)
        im.paste(icon, (820, 165), r)
        d = ImageDraw.Draw(im)
        d.text((80, 190), title, font=ImageFont.truetype(bold, 92), fill="#F3F5FA")
        d.text((84, 318), tag, font=ImageFont.truetype(reg, 38), fill="#C3C9D9")
        d.text((84, 520), "keefa.app", font=ImageFont.truetype(bold, 34), fill=a["accent"])
        im.save(ROOT / "assets" / f"og-{a['slug']}.png", optimize=True)
    # compress app icons
    for n in ("currencyx", "wayfare", "icon"):
        p = ROOT / "assets" / f"{n}.png"
        Image.open(p).convert("RGBA").resize((256, 256)).save(p, optimize=True)


def main():
    build_og()
    for lang in LANGS:
        build_keefa(lang)
        build_hub(lang)
        for a in APPS[1:]:
            build_app(lang, a)
    # de-duplicate sitemap paths (each path appended once per language)
    seen = []
    for p in SITEMAP:
        if p not in seen:
            seen.append(p)
    SITEMAP[:] = seen
    build_files()
    print("built:", ", ".join(SITEMAP))


if __name__ == "__main__":
    main()
