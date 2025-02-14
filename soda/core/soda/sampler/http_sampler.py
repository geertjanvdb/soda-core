from __future__ import annotations

import logging

import requests
from soda.sampler.sample_context import SampleContext
from soda.sampler.sample_ref import SampleRef
from soda.sampler.sampler import Sampler

logger = logging.getLogger(__name__)


class HTTPSampler(Sampler):
    def __init__(self, url: str, format: str = "json", link: str | None = None, message: str = ""):
        self.url = url
        self.format = format
        self.link = link
        self.message = message

    def store_sample(self, sample_context: SampleContext) -> SampleRef | None:

        logger.info(f"Sending failed row samples to {self.url}")
        sample_rows = sample_context.sample.get_rows()
        row_count = len(sample_rows)
        sample_schema = sample_context.sample.get_schema()

        result_dict = {"schema": sample_schema.get_dict(), "count": row_count, "rows": sample_rows}

        response = requests.post(self.url, json=result_dict)

        if response.status_code != 200:
            logger.error(f"Unable to upload failed rows to {self.url} -  {response.text}")
        else:
            logger.info(f"Uploaded {row_count} failed rows to {self.url}")

        if sample_context.samples_limit is not None:
            stored_row_count = row_count if row_count < sample_context.samples_limit else sample_context.samples_limit
        else:
            stored_row_count = row_count

        return SampleRef(
            name=sample_context.sample_name,
            schema=sample_schema,
            total_row_count=row_count,
            stored_row_count=stored_row_count,
            type="http",
            link=self.link,
            message=self.message,
        )
