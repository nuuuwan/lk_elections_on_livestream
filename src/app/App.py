import os
import tempfile
import time
from functools import cached_property
from urllib.parse import urlencode

from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from utils import Log

from utils_future import PNGFile

log = Log("App")
"""
http://localhost:3000/election?electionType=Parliamentary&date=2015-08-17
&nResultsDisplay=118&activeEntID=EC-04F
&lang=en
&groupBelowTheFold=Disclaimers&groupAggregatedResults=Electoral%20Districts&groupMonitoring=Turnout&groupModelInsights=Projected%20Result%20Details&=
"""


class App:

    def __init__(
        self,
        election_type="Parliamentary",
        date="2020-08-05",
        active_ent_id="EC-01C",
        lang="en",
        group_below_the_fold="Aggregated_Results",
        group_aggregated_results="Provinces",
        group_monitoring="Turnout",
        group_model_insights="Projected_Result_Details",
        is_local_mode=False,
    ):
        self.election_type = election_type
        self.date = date
        self.lang = lang
        self.active_ent_id = active_ent_id

        self.group_below_the_fold = group_below_the_fold
        self.group_aggregated_results = group_aggregated_results
        self.group_monitoring = group_monitoring
        self.group_model_insights = group_model_insights

        # other params
        self.is_local_mode = is_local_mode

        # selenium
        self.driver = None

    @cached_property
    def id(self):
        return f"{self.election_type}-{self.active_ent_id}"

    @cached_property
    def dir_output(self):
        dir_output = os.path.join(
            tempfile.gettempdir(),
            f"{self.election_type}.{self.date}",
            f"{self.active_ent_id}",
        )
        if not os.path.exists(dir_output):
            os.makedirs(dir_output)
        return dir_output

    @property
    def url_base(self):
        if self.is_local_mode:
            return "localhost:3000/election"
        return "https://nuuuwan.github.io/election"

    @property
    def url(self):
        params = dict(
            electionType=self.election_type,
            date=self.date,
            activeEntID=self.active_ent_id,
            lang=self.lang,
            groupBelowTheFold=self.group_below_the_fold,
            groupAggregatedResults=self.group_aggregated_results,
            groupMonitoring=self.group_monitoring,
            groupModelInsights=self.group_model_insights,
        )
        return f"{self.url_base}?{urlencode(params)}"

    def open_browser(self):
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
        zoom = 2

        driver.set_window_size(3200, 9600)
        log.debug(f'Opening "{self.url}"')
        driver.get(self.url)

        js_script = f"document.body.style.zoom='{zoom:.0%}'"
        driver.execute_script(js_script)
        self.driver = driver

        time.sleep(10)

    # "projection-details",
    # "latest-result-pd",
    # "latest-result-ed",
    # "latest-result-province",
    # "latest-result-lk",
    # "hexmap",
    # "aggregated-results-table-provinces",

    def download_screenshot(self, id):
        image_path = os.path.join(self.dir_output, f"{id}.png")
        if os.path.exists(image_path):
            log.debug(f"Already exists {image_path}")
            return image_path

        if not self.driver:
            self.open_browser()

        driver = self.driver
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.ID, id))
            )

            element = driver.find_element(By.ID, id)
            element.screenshot(image_path)
            PNGFile(image_path).add_padding(0.1).resize(
                1600, 900
            ).add_watermark(f"@lk_elections")

            log.debug(f"Wrote {image_path}")

            return image_path

        except WebDriverException:
            log.error(f"Failed to find {id}")

    def quit(self):
        if self.driver:
            self.driver.quit()
        self.driver = None
