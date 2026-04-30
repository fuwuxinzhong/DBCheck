from docx import Document
from lxml import etree
import zipfile

# 直接读 docx 的内部 XML，看 sectPr 实际在哪
path = r'D:\DBCheck\reports\MySQL巡检报告_MySQL_Server_20260428_172302.docx'
with zipfile.ZipFile(path) as z:
    doc_xml = z.read('word/document.xml')

root = etree.fromstring(doc_xml)
ns = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

# 找所有 sectPr
sectPrs = root.findall('.//{%s}sectPr' % ns)
print('sectPr count in XML: %d' % len(sectPrs))
for i, sp in enumerate(sectPrs):
    parent = sp.getparent()
    parent_tag = parent.tag.split('}')[1] if parent is not None else None
    print('  sectPr[%d]: parent=%s' % (i, parent_tag))

# 找 body 和它的子元素
body = root.find('{%s}body' % ns)
if body:
    children = list(body)
    child_tags = [c.tag.split('}')[1] for c in children]
    print('body child count: %d' % len(children))
    print('body children: %s' % child_tags[-5:])

# 用 python-docx 加载试试
doc = Document(path)
print()
print('python-docx view:')
print('  len(sections) = %d' % len(doc.sections))
print('  len(sectPr_lst) = %d' % len(doc._element.sectPr_lst))
try:
    s = doc.sections[-1]
    print('  sections[-1] = OK')
except Exception as e:
    print('  sections[-1] ERROR: %s' % e)
    print('  sectPr_lst content:')
    for i, sp in enumerate(doc._element.sectPr_lst):
        print('    [%d]: %s' % (i, sp.tag))
