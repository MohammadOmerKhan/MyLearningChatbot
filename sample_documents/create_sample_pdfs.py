#!/usr/bin/env python3

"""
Create sample financial documents for testing the document upload system.
This script generates realistic financial reports for the past 5 years (2019-2023).
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import os

def create_sample_document(year, company_name="TechCorp Solutions"):
    """Create a sample financial document for a given year"""
    
    # Create directory if it doesn't exist
    os.makedirs("/Users/omerkhan/Netsol Projects/Chatbot/sample_documents", exist_ok=True)
    
    filename = f"/Users/omerkhan/Netsol Projects/Chatbot/sample_documents/{company_name}_Annual_Report_{year}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=30)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, spaceAfter=12)
    
    # Title
    story.append(Paragraph(f"{company_name} Annual Financial Report {year}", title_style))
    story.append(Spacer(1, 12))
    
    # Executive Summary
    story.append(Paragraph("Executive Summary", heading_style))
    exec_summary = f"""
    {company_name} delivered strong financial performance in {year}, demonstrating resilience and growth 
    in a dynamic market environment. Our revenue growth of {10 + (year-2019)*3}% year-over-year reflects 
    our continued focus on innovation and customer satisfaction. The company maintained healthy profit 
    margins while investing significantly in research and development to drive future growth.
    
    Key highlights for {year} include expansion into new markets, successful product launches, and 
    strategic partnerships that position us well for continued success. Our commitment to operational 
    excellence and financial discipline has resulted in strong cash generation and improved shareholder returns.
    """
    story.append(Paragraph(exec_summary, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Financial Highlights
    story.append(Paragraph("Financial Highlights", heading_style))
    
    # Generate realistic financial data based on year
    base_revenue = 50000000  # $50M base
    growth_factor = 1 + (year - 2019) * 0.15  # 15% growth per year
    covid_impact = 0.85 if year == 2020 else 1.0  # COVID impact in 2020
    
    revenue = int(base_revenue * growth_factor * covid_impact)
    net_income = int(revenue * 0.12)  # 12% profit margin
    total_assets = int(revenue * 2.5)
    shareholders_equity = int(total_assets * 0.4)
    
    financial_data = [
        ['Metric', f'{year} ($000)', f'{year-1} ($000)', 'Change (%)'],
        ['Total Revenue', f'{revenue//1000:,}', f'{int(revenue*0.9)//1000:,}', '+11.1%'],
        ['Gross Profit', f'{int(revenue*0.6)//1000:,}', f'{int(revenue*0.9*0.58)//1000:,}', '+14.2%'],
        ['Operating Income', f'{int(revenue*0.15)//1000:,}', f'{int(revenue*0.9*0.13)//1000:,}', '+27.4%'],
        ['Net Income', f'{net_income//1000:,}', f'{int(net_income*0.85)//1000:,}', '+17.6%'],
        ['Total Assets', f'{total_assets//1000:,}', f'{int(total_assets*0.92)//1000:,}', '+8.7%'],
        ['Shareholders Equity', f'{shareholders_equity//1000:,}', f'{int(shareholders_equity*0.88)//1000:,}', '+13.6%'],
    ]
    
    table = Table(financial_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 20))
    
    # Business Segments
    story.append(Paragraph("Business Segment Performance", heading_style))
    segment_text = f"""
    Our three main business segments all contributed to strong performance in {year}:
    
    • Software Solutions: Generated ${int(revenue*0.5)//1000:,}K in revenue, representing 50% of total revenue. 
      This segment showed robust growth driven by increased demand for digital transformation solutions.
    
    • Consulting Services: Contributed ${int(revenue*0.3)//1000:,}K in revenue (30% of total). Our consulting 
      business benefited from strong client relationships and expanded service offerings.
    
    • Cloud Infrastructure: Delivered ${int(revenue*0.2)//1000:,}K in revenue (20% of total). This growing 
      segment showed the highest growth rate at 25% year-over-year.
    """
    story.append(Paragraph(segment_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Future Outlook
    story.append(Paragraph("Future Outlook", heading_style))
    outlook_text = f"""
    Looking ahead to {year+1}, {company_name} is well-positioned for continued growth. We expect:
    
    • Revenue growth of 12-15% driven by new product launches and market expansion
    • Continued investment in R&D to maintain our competitive advantage
    • Strategic acquisitions to accelerate growth in key markets
    • Focus on operational efficiency to maintain healthy profit margins
    
    Our strong balance sheet and cash position provide flexibility to pursue growth opportunities 
    while returning value to shareholders through dividends and share repurchases.
    """
    story.append(Paragraph(outlook_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Key Metrics Summary
    story.append(Paragraph("Key Performance Indicators", heading_style))
    kpi_data = [
        ['KPI', f'{year}', f'{year-1}', 'Target {}'.format(year+1)],
        ['Revenue Growth (%)', '11.1%', '8.5%', '12-15%'],
        ['Profit Margin (%)', '12.0%', '11.2%', '12-13%'],
        ['Return on Equity (%)', f'{(net_income/shareholders_equity*100):.1f}%', '28.5%', '>30%'],
        ['Cash Flow from Operations ($M)', f'${int(revenue*0.18)//1000000}', f'${int(revenue*0.9*0.16)//1000000}', f'${int(revenue*1.15*0.19)//1000000}'],
        ['Employee Count', f'{1200 + (year-2019)*150}', f'{1200 + (year-2020)*150}', f'{1200 + (year-2018)*150}'],
    ]
    
    kpi_table = Table(kpi_data)
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(kpi_table)
    
    # Build the PDF
    doc.build(story)
    print(f"Created: {filename}")

def create_netsol_specific_document(year):
    """Create a Netsol-specific financial document"""
    
    filename = f"/Users/omerkhan/Netsol Projects/Chatbot/sample_documents/NetSol_Technologies_Annual_Report_{year}.pdf"
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=18, spaceAfter=30)
    heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=14, spaceAfter=12)
    
    # Title
    story.append(Paragraph(f"NetSol Technologies Limited Annual Report {year}", title_style))
    story.append(Spacer(1, 12))
    
    # Company Overview
    story.append(Paragraph("Company Overview", heading_style))
    overview_text = f"""
    NetSol Technologies Limited is a leading provider of enterprise software solutions for the global finance 
    and leasing industry. Founded in 1997, the company has established itself as a pioneer in developing 
    innovative technology solutions that help financial institutions streamline their operations and enhance 
    customer experiences.
    
    In {year}, NetSol continued to expand its global footprint with offices in Pakistan, USA, UK, China, 
    and Thailand. Our flagship product, NFS Ascent, remains the industry-leading platform for automotive 
    finance, equipment finance, and microfinance institutions worldwide.
    """
    story.append(Paragraph(overview_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Financial Performance
    story.append(Paragraph("Financial Performance", heading_style))
    
    # Generate Netsol-specific financial data
    base_revenue = 25000000  # $25M base for Netsol
    growth_factor = 1 + (year - 2019) * 0.12  # 12% growth per year
    covid_impact = 0.88 if year == 2020 else 1.0
    
    revenue = int(base_revenue * growth_factor * covid_impact)
    net_income = int(revenue * 0.08)  # 8% profit margin (software company)
    total_assets = int(revenue * 1.8)
    shareholders_equity = int(total_assets * 0.45)
    
    netsol_financial = [
        ['Financial Metric', f'FY {year} (USD)', f'FY {year-1} (USD)', 'Growth'],
        ['Net Revenue', f'${revenue//1000:,}K', f'${int(revenue*0.91)//1000:,}K', '+9.9%'],
        ['Software License Revenue', f'${int(revenue*0.4)//1000:,}K', f'${int(revenue*0.91*0.38)//1000:,}K', '+15.3%'],
        ['Maintenance & Support', f'${int(revenue*0.35)//1000:,}K', f'${int(revenue*0.91*0.36)//1000:,}K', '+7.2%'],
        ['Professional Services', f'${int(revenue*0.25)//1000:,}K', f'${int(revenue*0.91*0.26)//1000:,}K', '+6.4%'],
        ['Gross Profit', f'${int(revenue*0.65)//1000:,}K', f'${int(revenue*0.91*0.62)//1000:,}K', '+16.5%'],
        ['Net Income', f'${net_income//1000:,}K', f'${int(net_income*0.85)//1000:,}K', '+17.6%'],
        ['Total Assets', f'${total_assets//1000:,}K', f'${int(total_assets*0.94)//1000:,}K', '+6.4%'],
    ]
    
    financial_table = Table(netsol_financial)
    financial_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(financial_table)
    story.append(Spacer(1, 20))
    
    # Product Portfolio
    story.append(Paragraph("Product Portfolio", heading_style))
    products_text = f"""
    NetSol's comprehensive product suite continued to drive growth in {year}:
    
    • NFS Ascent Platform: Our flagship auto finance solution processed over $12 billion in loan 
      originations during {year}, serving major financial institutions across North America, Europe, and Asia.
    
    • LeasePak: The leasing solution showed strong adoption with 15 new implementations, particularly 
      in the equipment finance sector.
    
    • Apparo: Our mobile-first solution for emerging markets gained significant traction with 8 new 
      deployments in Asia and Africa.
    
    • WholesalePro: The dealer management system expanded its market share with enhanced features 
      for inventory management and customer relationship management.
    
    Total active installations reached {180 + (year-2019)*25} across {45 + (year-2019)*3} countries, 
    representing a {round((25/180)*100, 1)}% increase in our global footprint.
    """
    story.append(Paragraph(products_text, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Regional Performance
    story.append(Paragraph("Regional Performance", heading_style))
    regional_data = [
        ['Region', 'Revenue Share', f'{year} Growth', 'Key Achievements'],
        ['North America', '45%', '+12%', 'Tier-1 bank implementation'],
        ['Europe', '25%', '+8%', 'Brexit compliance updates'],
        ['Asia Pacific', '20%', '+18%', 'China market expansion'],
        ['Middle East & Africa', '10%', '+15%', 'New Islamic finance features'],
    ]
    
    regional_table = Table(regional_data)
    regional_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.lightcyan),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(regional_table)
    
    # Build the PDF
    doc.build(story)
    print(f"Created: {filename}")

if __name__ == "__main__":
    print("Creating sample financial documents for testing...")
    
    # Create general tech company documents
    for year in range(2019, 2024):
        create_sample_document(year, "TechCorp Solutions")
    
    # Create NetSol-specific documents
    for year in range(2019, 2024):
        create_netsol_specific_document(year)
    
    print("\nSample documents created successfully!")
    print("Location: /Users/omerkhan/Netsol Projects/Chatbot/sample_documents/")
    print("\nDocuments created:")
    print("• TechCorp Solutions Annual Reports (2019-2023)")
    print("• NetSol Technologies Annual Reports (2019-2023)")
    print("\nYou can now test the document upload system with these PDFs!")
