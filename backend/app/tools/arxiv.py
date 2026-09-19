import httpx
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus


ARXIV_API = 'https://export.arxiv.org/api/query'


def _text_or_none(elem, tag=None):
	if elem is None:
		return None
	return elem.text if tag is None else (elem.find(tag).text if elem.find(tag) is not None else None)


def search_papers(query: str, limit: int = 10) -> list[dict]:
	"""Search arXiv for papers matching `query`.

	Returns list of dicts with title, abstract, authors (list), year, url.
	"""
	params = {
		'search_query': f'all:{query}',
		'start': 0,
		'max_results': limit,
	}
	url = f"{ARXIV_API}?search_query={quote_plus('all:' + query)}&start=0&max_results={limit}"
	resp = httpx.get(url, timeout=10.0, follow_redirects=True)
	resp.raise_for_status()
	text = resp.text
	# Parse Atom XML
	root = ET.fromstring(text)
	ns = {'atom': 'http://www.w3.org/2005/Atom'}
	entries = []
	for entry in root.findall('atom:entry', ns):
		title = entry.find('atom:title', ns)
		summary = entry.find('atom:summary', ns)
		published = entry.find('atom:published', ns)
		authors = [a.find('atom:name', ns).text for a in entry.findall('atom:author', ns) if a.find('atom:name', ns) is not None]
		link = None
		for l in entry.findall('atom:link', ns):
			if l.attrib.get('type') == 'text/html':
				link = l.attrib.get('href')
				break
		# fallback to id
		if not link:
			id_elem = entry.find('atom:id', ns)
			link = id_elem.text if id_elem is not None else None

		year = None
		if published is not None and published.text:
			try:
				year = int(published.text[:4])
			except Exception:
				year = None

		entries.append({
			'title': title.text.strip() if title is not None and title.text else None,
			'abstract': summary.text.strip() if summary is not None and summary.text else None,
			'authors': authors,
			'year': year,
			'url': link,
		})

	return entries
