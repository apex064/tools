from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
import os

path = "Chima_Chidiebere_Sunday_Nomba_SRE_Cover_Letter.pdf"
base = getSampleStyleSheet()
name = ParagraphStyle("Name", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=17, leading=20, spaceAfter=2)
meta = ParagraphStyle("Meta", parent=base["Normal"], fontName="Helvetica", fontSize=8.5, leading=12, textColor=colors.HexColor("#444444"), spaceAfter=2)
date = ParagraphStyle("Date", parent=meta, spaceBefore=13, spaceAfter=13)
subject = ParagraphStyle("Subject", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=10, leading=13, spaceBefore=3, spaceAfter=11)
body = ParagraphStyle("Body", parent=base["Normal"], fontName="Helvetica", fontSize=9.5, leading=14.2, textColor=colors.HexColor("#222222"), spaceAfter=9)
closing = ParagraphStyle("Closing", parent=body, spaceBefore=2, spaceAfter=2)

story = [
    Paragraph("CHIMA CHIDIEBERE SUNDAY", name),
    Paragraph("Full-Stack Software Engineer | Backend &amp; Systems Development", meta),
    Paragraph("Nigeria &nbsp;•&nbsp; github.com/apex064 &nbsp;•&nbsp; apex064.earncentive.com", meta),
    Spacer(1, 5),
    HRFlowable(width="100%", thickness=0.8, color=colors.black, spaceBefore=4, spaceAfter=7),
    Paragraph("31 October 2026", date),
    Paragraph("Hiring Team<br/>Nomba", meta),
    Spacer(1, 8),
    Paragraph("Application for Site Reliability Engineer", subject),
    Paragraph("Dear Hiring Team,", body),
    Paragraph(
        "I am writing to apply for the Site Reliability Engineer role at Nomba. I am a software engineer "
        "with more than five years of experience building and supporting web, backend, and mobile products. "
        "My work has involved developing production applications, designing APIs and data systems, "
        "troubleshooting service issues, and improving the reliability of the systems behind user-facing "
        "products. I am interested in bringing that practical engineering experience to a fintech platform "
        "operating at Nomba’s scale.", body),
    Paragraph(
        "In my role at Earncentive, I develop and maintain applications across frontend and backend services, "
        "integrate external platforms such as payment gateways, and work through testing, debugging, and "
        "performance issues. I have also worked with Python, Django, Flask, Node.js, PostgreSQL, MySQL, "
        "Redis, and Linux. This combination has given me a useful understanding of how application code, "
        "data stores, integrations, and the underlying runtime environment affect the reliability of a "
        "complete service.", body),
    Paragraph(
        "I have also taken responsibility for building and operating products beyond feature development. "
        "Through my work on FLINK and other applications, I have dealt with backend services, asynchronous "
        "workers, WebSocket-based functionality, deployment processes, server logs, and production "
        "troubleshooting in Linux environments. At Mattys Inc., I led development of a web application "
        "serving more than 100,000 users, built REST APIs with Django REST Framework, improved database "
        "query performance by 40%, and implemented a GitHub Actions CI/CD pipeline. These experiences "
        "have strengthened my ability to investigate failures, identify bottlenecks, and make changes "
        "that improve system behaviour.", body),
    Paragraph(
        "What attracts me to Nomba is the engineering challenge behind dependable financial infrastructure. "
        "When businesses and individuals rely on a platform for payments and everyday financial operations, "
        "availability, security, observability, and disciplined incident response are essential. I would "
        "welcome the opportunity to work closely with your engineering teams to improve operational "
        "visibility, automate repeatable tasks, strengthen deployment practices, and build systems that "
        "remain dependable as usage grows.", body),
    Paragraph(
        "I bring a strong foundation in Python and Linux-based systems, practical experience with databases "
        "and production application support, and a product-minded approach to engineering. I am also "
        "committed to deepening my expertise in formal SRE practices and infrastructure automation. "
        "I would appreciate the opportunity to discuss how my background could contribute to Nomba’s "
        "reliability and infrastructure goals.", body),
    Paragraph("Thank you for your time and consideration.", body),
    Paragraph("Yours sincerely,", closing),
    Spacer(1, 16),
    Paragraph("<b>Chima Chidiebere Sunday</b>", closing),
]

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#BBBBBB"))
    canvas.setLineWidth(0.4)
    canvas.line(22*mm, 15*mm, A4[0]-22*mm, 15*mm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#666666"))
    canvas.drawString(22*mm, 10*mm, "APPLICATION — SITE RELIABILITY ENGINEER")
    canvas.drawRightString(A4[0]-22*mm, 10*mm, str(doc.page))
    canvas.restoreState()

pdf = SimpleDocTemplate(path, pagesize=A4, rightMargin=22*mm, leftMargin=22*mm,
                        topMargin=18*mm, bottomMargin=22*mm,
                        title="Cover Letter - Chima Chidiebere Sunday - Nomba SRE",
                        author="Chima Chidiebere Sunday")
pdf.build(story, onFirstPage=footer, onLaterPages=footer)
print("Created:", path, "size:", os.path.getsize(path))
