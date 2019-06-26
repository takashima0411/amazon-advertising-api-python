from setuptools import setup
import amazon_advertising_api.versions as aa_versions


setup(
    name='amazon_advertising_api',
    packages=['amazon_advertising_api'],
    version=aa_versions.versions['application_version'],
    description='Amazon Advertising API client https://advertising.amazon.com/API/docs/v2/reference/profiles?ref_=a20m_us_api_dc2',
    url='https://github.com/takashima0411/amazon-advertising-api-python')
