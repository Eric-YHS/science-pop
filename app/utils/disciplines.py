DISCIPLINES = [
    {
        "slug": "ai",
        "name": "人工智能与计算机科学",
        "sources": [
            {"name": "arXiv.org", "url": "https://arxiv.org", "type": "api"},
            {"name": "asXiv.org", "url": "https://asxiv.org", "type": "web"},
        ],
    },
    {
        "slug": "life_science",
        "name": "生命科学与健康",
        "sources": [
            {"name": "PubMed Central", "url": "https://www.ncbi.nlm.nih.gov/pmc/", "type": "api"},
            {"name": "PLOS", "url": "https://www.plos.org/", "type": "api"},
            {"name": "SinoMed", "url": "http://www.sinomed.ac.cn/", "type": "web"},
            {"name": "HighWire Press", "url": "https://www.highwirepress.com/", "type": "web"},
            {"name": "BiomedRxiv", "url": "https://www.biomedrxiv.org.cn/", "type": "web"},
        ],
    },
    {
        "slug": "neuroscience",
        "name": "脑科学与心理学",
        "sources": [
            {"name": "Brain and Behavior", "url": "https://onlinelibrary.wiley.com/journal/21579032", "type": "web"},
            {"name": "Annals of General Psychiatry", "url": "https://annals-general-psychiatry.biomedcentral.com/", "type": "web"},
            {"name": "PCI Neuroscience", "url": "https://neuroscience.peercommunityin.org/", "type": "web"},
            {"name": "Open Mind", "url": "https://direct.mit.edu/opmi", "type": "web"},
        ],
    },
    {
        "slug": "social_science",
        "name": "社会与行为科学",
        "sources": [
            {"name": "国家哲学社会科学文献中心", "url": "http://www.ncpssd.org/", "type": "web"},
            {"name": "SSRN", "url": "https://www.ssrn.com/", "type": "web"},
            {"name": "RePEc", "url": "https://repec.org/", "type": "api"},
            {"name": "IMF eLibrary", "url": "https://www.elibrary.imf.org/", "type": "web"},
        ],
    },
    {
        "slug": "economics",
        "name": "经济金融",
        "sources": [
            {"name": "CnOpenData", "url": "https://www.cnopendata.com/", "type": "web"},
            {"name": "RePEc", "url": "https://repec.org/", "type": "api"},
            {"name": "国泰安CSMAR", "url": "https://www.gtarsc.com/", "type": "web"},
        ],
    },
    {
        "slug": "environment",
        "name": "环境与气候科学",
        "sources": [
            {"name": "GreenFILE", "url": "https://www.ebsco.com/products/research-databases/greenfile", "type": "web"},
            {"name": "OpenSky", "url": "https://opensky.ucar.edu/", "type": "web"},
            {"name": "Environment Complete", "url": "https://www.ebsco.com/products/research-databases/environment-complete", "type": "web"},
        ],
    },
]

SOURCE_DISCIPLINE_MAP = {}
for disc in DISCIPLINES:
    for source in disc["sources"]:
        SOURCE_DISCIPLINE_MAP[source["name"]] = disc["slug"]
