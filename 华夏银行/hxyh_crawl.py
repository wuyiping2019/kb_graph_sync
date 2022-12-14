from requests import Session
from crawl import MutiThreadCrawl
from utils.global_config import get_table_name
from utils.spider_flow import SpiderFlow, process_flow
from hxyh_config import MASK, LOG_NAME
from 华夏银行.hxyh_mobile import hxyh_crawl_mobile
from 华夏银行.hxyh_pc import hxyh_crawl_pc


class SpiderFlowImpl(SpiderFlow):
    def callback(self, session: Session, log_id: int, muti_thread_crawl: MutiThreadCrawl, **kwargs):
        hxyh_crawl_pc.init_props(session=session,
                                 log_id=log_id,
                                 muti_thread_crawl=muti_thread_crawl,
                                 **kwargs)
        hxyh_crawl_mobile.init_props(session=session,
                                     log_id=log_id,
                                     muti_thread_crawl=muti_thread_crawl,
                                     **kwargs)
        try:

            hxyh_crawl_pc.do_crawl()
            hxyh_crawl_mobile.do_crawl()
            hxyh_crawl_mobile.processed_rows = hxyh_crawl_mobile.processed_rows + hxyh_crawl_pc.processed_rows
            hxyh_crawl_mobile.do_save()
        except Exception as e:
            raise e
        finally:
            hxyh_crawl_pc.close()
            hxyh_crawl_mobile.close()


def do_crawl(self: MutiThreadCrawl):
    process_flow(
        log_name=LOG_NAME,
        target_table=get_table_name(mask=MASK),
        callback=SpiderFlowImpl(),
        muti_thread_crawl=self
    )
