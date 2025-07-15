import feedparser, re, smtplib, os, time, schedule
from email.message import EmailMessage
from datetime import date, datetime

# --- CONFIGURA ---
KEYWORDS = re.compile(r"(remote|telecommute|work from home).*(junior|entry.level|graduate|associate|trainee)?.*(data scientist|data engineer|quantitative developer|quant developer|quantitative analyst|quant analyst)|"
                     r"(junior|entry.level|graduate|associate|trainee).*(data scientist|data engineer|quantitative developer|quant developer|quantitative analyst|quant analyst).*(remote|telecommute|work from home)|"
                     r"(data scientist|data engineer|quantitative developer|quant developer|quantitative analyst|quant analyst).*(junior|entry.level|graduate|associate|trainee).*(remote|telecommute|work from home)|"
                     r"python.*(junior|entry.level|graduate|associate|trainee)?.*(data scientist|data engineer|quantitative developer|quant developer)", re.I)
FEEDS = [
    # WeWorkRemotely - Enfocado en data y desarrollo
    "https://weworkremotely.com/categories/remote-data-jobs.rss",
    "https://weworkremotely.com/categories/remote-programming-jobs.rss",
    
    # RemoteOK - Específico para data science, quant y data engineering
    "https://remoteok.com/remote-data-science-jobs.rss",
    "https://remoteok.com/remote-data-engineer-jobs.rss",
    "https://remoteok.com/remote-python-jobs.rss",
    "https://remoteok.com/remote-quantitative-jobs.rss",
    "https://remoteok.com/remote-analyst-jobs.rss",
    
    # AngelList/Wellfound - Startups con roles junior
    "https://angel.co/job_listings.rss?locations%5B%5D=1688-remote",
    
    # Stackoverflow Jobs
    "https://stackoverflow.com/jobs/feed?r=true&q=python+data+remote",
    
    # RemoteOK con términos específicos
    "https://remoteok.com/remote-jobs.rss?q=junior+data+scientist",
    "https://remoteok.com/remote-jobs.rss?q=entry+level+data+engineer",
    "https://remoteok.com/remote-jobs.rss?q=quantitative+developer",
    
    # JustRemote - Enfocado en data
    "https://justremote.co/remote-jobs.rss?q=data+scientist",
    "https://justremote.co/remote-jobs.rss?q=data+engineer",
    
    # Remote.co - Desarrolladores
    "https://remote.co/remote-jobs/developer/?feed=rss2",
    
    # Working Nomads - General
    "https://www.workingnomads.co/jobs.rss",
    
    # NoDesk - Trabajos remotos
    "https://nodesk.co/remote-jobs/rss.xml",
    
    # RemoteJobs.com - General
    "https://remotejobs.com/rss",
]
EMAIL_FROM = os.getenv("EMAIL_FROM")
EMAIL_TO = os.getenv("EMAIL_TO")
APP_PASSWORD = os.getenv("APP_PASSWORD")  # App Password desde variables de entorno
# -----------------

def find_matches():
    matches = []
    seen_links = set()  # Para evitar duplicados
    
    print(f"Searching {len(FEEDS)} RSS feeds...")
    
    for i, url in enumerate(FEEDS, 1):
        try:
            print(f"[{i}/{len(FEEDS)}] Checking feed...")
            feed = feedparser.parse(url)
            
            if hasattr(feed, 'bozo') and feed.bozo:
                print(f"[{i}/{len(FEEDS)}] Feed has parsing issues, skipping")
                continue
                
            entries_count = len(feed.entries)
            print(f"[{i}/{len(FEEDS)}] Found {entries_count} entries")
                
            for entry in feed.entries:
                # Evitar duplicados por URL
                if entry.link in seen_links:
                    continue
                    
                if KEYWORDS.search(entry.title) or (hasattr(entry, 'description') and KEYWORDS.search(entry.description)):
                    matches.append(f"• {entry.title}\n  {entry.link}")
                    seen_links.add(entry.link)
                    print(f"[{i}/{len(FEEDS)}] ✅ Match found: {entry.title[:50]}...")
                    
        except Exception as e:
            print(f"[{i}/{len(FEEDS)}] Error: {str(e)}")
            continue
            
    return matches

def send_email(lines):
    if not lines:
        return
        
    try:
        msg = EmailMessage()
        msg["Subject"] = f"Job digest – {date.today()}"
        msg["From"] = EMAIL_FROM
        msg["To"] = EMAIL_TO
        
        # Crear contenido más legible
        content = f"Found {len(lines)} remote Python jobs:\n\n"
        content += "\n\n".join(lines)
        content += f"\n\n---\nGenerated on {date.today()}"
        
        msg.set_content(content)
        
        # Detectar el proveedor de email y usar el servidor SMTP correcto
        if "gmail.com" in EMAIL_FROM:
            smtp_server = "smtp.gmail.com"
            smtp_port = 465
        elif "hotmail.com" in EMAIL_FROM or "outlook.com" in EMAIL_FROM or "live.com" in EMAIL_FROM:
            smtp_server = "smtp.office365.com"
            smtp_port = 587
        else:
            # Default a Gmail
            smtp_server = "smtp.gmail.com"
            smtp_port = 465
        
        if smtp_port == 587:
            # Para Outlook/Hotmail usar STARTTLS
            with smtplib.SMTP(smtp_server, smtp_port) as smtp:
                smtp.starttls()
                smtp.login(EMAIL_FROM, APP_PASSWORD)
                smtp.send_message(msg)
                print("Email sent ✅")
        else:
            # Para Gmail usar SSL
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
                smtp.login(EMAIL_FROM, APP_PASSWORD)
                smtp.send_message(msg)
                print("Email sent ✅")
            
    except Exception as e:
        print(f"Email error: {str(e)}")
        raise

def run_bot():
    """Ejecuta el bot una vez"""
    print(f"=== JOB BOT STARTED === {datetime.now()}")
    print(f"EMAIL_FROM: {EMAIL_FROM}")
    print(f"EMAIL_TO: {EMAIL_TO}")
    print(f"APP_PASSWORD: {'*' * len(APP_PASSWORD) if APP_PASSWORD else 'None'}")
    print(f"Total feeds: {len(FEEDS)}")
    
    jobs = find_matches()
    print(f"Found {len(jobs)} total jobs")
    
    if jobs:
        print("Sending email...")
        send_email(jobs)
        print(f"✅ Process completed! Sent {len(jobs)} jobs.")
    else:
        print("❌ No jobs found matching criteria.")
        
    print(f"=== JOB BOT FINISHED === {datetime.now()}")

if __name__ == "__main__":
    print("🚀 Job Bot Worker Service Started")
    print("⏰ Scheduled to run at 8:00 AM and 8:00 PM VET")
    print("🌍 VET = UTC-4, so running at 12:00 PM and 12:00 AM UTC")
    
    # Programar las ejecuciones
    schedule.every().day.at("12:00").do(run_bot)  # 8:00 AM VET
    schedule.every().day.at("00:00").do(run_bot)  # 8:00 PM VET
    
    # Ejecutar inmediatamente para probar
    print("🧪 Running test execution...")
    run_bot()
    
    print("⏳ Worker ready, waiting for scheduled times...")
    
    # Loop principal
    while True:
        schedule.run_pending()
        time.sleep(60)  # Revisar cada minuto
