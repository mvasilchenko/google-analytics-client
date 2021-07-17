import datetime

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials
from typing import List
import pandas as pd


class GoogleAnalyticsClient:
    """
    Instance of client
    """
    SCOPES = ["https://www.googleapis.com/auth/analytics.readonly"]
    API_NAME = "analyticsreporting"
    API_VERSIONS = "v4"

    def __init__(self,
                 json_file: str,
                 view_id: str,
                 start_date: datetime.date,
                 end_date: datetime.date,
                 ):
        """

        :param json_file:str a filename where stored credentials
        :param view_id:str google analytics view id
        :param start_date:datetime.date start date
        :param end_date: datetime.date end date
        """
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(json_file, scopes=self.SCOPES)
        self.client = build()
        self.view_id = view_id
        self.start_date = start_date
        self.end_date = end_date

    def generate_request(self, **kwargs) -> dict:
        """
        func what generate request body for google analytics
        :param kwargs: params
        :return:dict where stored prepared parameters for request to google analytics
        """
        body = {
            "viewId": self.view_id,
            "dateRanges": {"starDate": self.start_date, "endDate": self.end_date},
            "dimensions": self.generate_dimensions(kwargs.get("dimensions"), bool(kwargs.get("segments"))),
            "metrics": self.generate_metrics(kwargs.get("metrics")),
            "filtersExpression": kwargs.get("filter"),
            "pageToken": kwargs.get("pageToken"),
            "samplingLevel": "LARGE",
            "includeEmptyRows": kwargs.get("include_empty_rows", True),
            "segments": [{"segment_id": kwargs.get("segments")}] if kwargs.get("segments") else None,
            "pageSize": "100000",
        }

        return body

    def generate_dimensions(self, dimensions: list, segments: bool) -> List[dict]:
        """
        func which prepared your dimensions for a google analytics query
        :param dimensions:list
        :param segments:bool
        :return:List[dict]
        """
        dimensions = list(map(lambda x: {"name": x}, dimensions))
        if segments:
            dimensions.append({"name": "ga:segment"})
        return dimensions

    def generate_metrics(self, metrics: list) -> List[dict]:
        """
        func which prepared your metrics for a google analytics query
        :param metrics:list
        :return:List[dict]
        """
        return list(map(lambda x: {"expression": x}, metrics))

    def parse_response(self, response) -> dict:
        """
        func which parsed returned response from google analytics
        :param response:
        :return:
        """
        report = response.get("reports")[0]
        report_data = report.get("data", {})

        result = {}
        data = []
        headers = []

        column_headers = report.get("columnHeader", {})
        metric_headers = column_headers.get("metricHeader", {}).get(
            "metricHeaderEntries", []
        )
        dimension_headers = column_headers.get("dimensions", [])

        headers.extend(
            [dimension_header for dimension_header in dimension_headers]
        )
        headers.extend(
            [metric_header["name"] for metric_header in metric_headers]
        )

        rows = report_data.get("rows", [])
        for row in rows:
            row_result = []
            dimensions = row.get("dimensions", [])
            metrics = row.get("metrics", [])
            row_result.extend(
                [dimension for dimension in dimensions]
            )
            row_result.extend(
                [metric for metric in metrics[0]["values"]]
            )
            data.append(row_result)

        df = pd.DataFrame(data, columns=headers)
        df.columns = df.columns.str.replace("ga:", "")

        if report_data.get("samplesReadCounts"):
            samples_read_counts = int(report_data.get("samplesReadCounts", [])[0])
            sampling_space_sizes = int(report_data.get("samplingSpaceSizes", [])[0])
        else:
            samples_read_counts = None
            sampling_space_sizes = None
        result["info"] = {
            "isDataGolden": report["data"].get("isDataGolden", False),
            "nextPageToken": report.get("nextPageToken"),
            "samplesReadCounts": samples_read_counts,
            "samplingSpaceSizes": sampling_space_sizes,
        }
        result["data"] = df
        return result

    def fetch(self, **kwargs) -> dict or None:
        request_body = self.generate_request(**kwargs)
        response = (
            self.client.reports().batchGet(body={"reportRequests": request_body}).execute()
        )
        parsed = self.parse_response(response)
        yield parsed["data"]
        kwargs["pageToken"] = parsed.get("info", {}).get("nextPageToken", None)
        self.fetch(**kwargs)
        if not kwargs["pageToken"]:
            response["info"] = parsed.get("info")
            return
