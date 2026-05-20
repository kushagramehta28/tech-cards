from scraper.morningbrew.main import main as main_morningbrew
from scraper.techbrew.main import main as main_techbrew
from scraper.thebrutalistreport.main import main as main_brutalist_report

from dotenv import load_dotenv
load_dotenv()  # This injects the HF_TOKEN directly into os.environ automatically

main_brutalist_report()
main_morningbrew()
main_techbrew()
