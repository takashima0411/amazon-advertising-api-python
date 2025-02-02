from amazon_advertising_api.regions import regions
from amazon_advertising_api.versions import versions
from io import BytesIO
import urllib.request
import urllib.parse
import gzip
import json


class AdvertisingApi:
    """Lightweight client library for Amazon Sponsored Products API."""

    def __init__(self,
                 client_id,
                 client_secret,
                 region,
                 access_token=None,
                 refresh_token=None,
                 sandbox=False):
        """
        Client initialization.

        :param client_id: Login with Amazon client Id that has been whitelisted
            for cpc_advertising:campaign_management
        :type client_id: string
        :param client_secret: Login with Amazon client secret key.
        :type client_id: string
        :param region: Region code for endpoint. See regions.py.
        :type region: string
        :param access_token: The access token for the advertiser account.
        :type access_token: string
        :param refresh_token: The refresh token for the advertiser account.
        :type refresh_token: string
        :param sandbox: Indicate whether you are operating in sandbox or prod.
        :type sandbox: boolean
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self._access_token = access_token
        self.refresh_token = refresh_token

        self.api_version = versions['api_version']
        self.user_agent = 'AdvertisingAPI Python Client Library v{}'.format(
            versions['application_version'])
        self.profile_id = None
        self.token_url = None

        if self._access_token is None and self.refresh_token is None:
            raise ValueError('access_token and refresh_token is empty. need at least one of them.')

        if region in regions:
            if sandbox:
                self.endpoint = regions[region]['sandbox']
            else:
                self.endpoint = regions[region]['prod']
            self.token_url = regions[region]['token_url']
        else:
            raise KeyError('Region {} not found in regions.'.format(regions))
        if self._access_token is None and self.refresh_token is None:
            raise ('Region {} not found in regions.'.format(regions))

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, value):
        """Set access_token"""
        self._access_token = value

    def do_refresh_token(self):
        if self.refresh_token is None:
            return {'success': False,
                    'code': 0,
                    'response': 'refresh_token is empty.'}

        self._access_token = urllib.parse.unquote(self._access_token)
        self.refresh_token = urllib.parse.unquote(self.refresh_token)

        params = {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret}

        data = urllib.parse.urlencode(params)

        req = urllib.request.Request(
            url='https://{}'.format(self.token_url),
            data=data.encode('utf-8'))

        try:
            f = urllib.request.urlopen(req)
            response = f.read().decode('utf-8')
            if 'access_token' in response:
                json_data = json.loads(response)
                self._access_token = json_data['access_token']
                return {'success': True,
                        'code': f.code,
                        'response': self._access_token}
            else:
                return {'success': False,
                        'code': f.code,
                        'response': 'access_token not in response.'}
        except urllib.error.HTTPError as e:
            return {'success': False,
                    'code': e.code,
                    'response': e.msg}

    def get_profiles(self):
        """
        Retrieves profiles associated with an auth token.

        :GET: /profiles
        :returns:
            :200: Success
            :401: Unauthorized
        """
        interface = 'profiles'
        return self._operation(interface)

    def get_profile(self, profile_id):
        """
        Retrieves a single profile by Id.

        :GET: /profiles/{profileId}
        :param profile_id: The Id of the requested profile.
        :type profile_id: string
        :returns:
            :200: List of **Profile**
            :401: Unauthorized
            :404: Profile not found
        """
        interface = 'profiles/{}'.format(profile_id)
        return self._operation(interface)

    def set_profile(self, profile_id):
        """
        Setting scope of requests

        :param profile_id:
        :type profile_id: string
        :return:
            setted profile_id
        """
        self.profile_id = str(profile_id)
        return self.profile_id

    def update_profiles(self, data):
        """
        Updates one or more profiles. Advertisers are identified using their
        profileIds.

        :PUT: /profiles
        :param data: A list of updates containing **proflileId** and the
            mutable fields to be modified. Only daily budgets are mutable at
            this time.
        :type data: List of **Profile**

        :returns:
            :207: List of **ProfileResponse** reflecting the same order as the
                input
            :401: Unauthorized
        """
        interface = 'profiles'
        return self._operation(interface, data, method='PUT')

    def get_portfolios(self):
        """
        Retrieve a list of up to 100 portfolios using the specified filters.
        :return:
            :200: Portfolio
            :401: Unauthorized
            :404: Portfolio not found
        """
        interface = 'portfolios'

        return self._operation(interface)

    def get_portfolio(self, portfolio_id):
        """
        Retrieve a list of up to 100 portfolios using the specified filters.
        :return:
            :200: Portfolio
            :401: Unauthorized
            :404: Portfolio not found
        """
        interface = 'portfolios/{}'.format(portfolio_id)
        return self._operation(interface)

    def get_portfolios_ex(self):
        """
        Retrieve a list of up to 100 portfolios using the specified filters.
        :return:
            :200: Portfolio
            :401: Unauthorized
            :404: Portfolio not found
        """
        interface = 'portfolios/extended'
        return self._operation(interface)

    def get_portfolio_ex(self, portfolio_id):
        """
        Retrieve a list of up to 100 portfolios using the specified filters.
        :return:
            :200: Portfolio
            :401: Unauthorized
            :404: Portfolio not found
        """
        interface = 'portfolios/extended/{}'.format(portfolio_id)
        return self._operation(interface)

    def create_portfolio(self, data):
        """
        Create one or more portfolios. Maximum number of portfolios per account is 100.

        :param data:

        :return:
            :200: Portfolio
            :401: Unauthorized
            :404: Portfolio not found
        """
        interface = 'portfolios'
        return self._operation(interface, data, 'POST')

    def update_portfolio(self, data):
        """
        Update one or more portfolios.
        :param data:

        :return:
            :200: Portfolio
            :401: Unauthorized
            :404: Portfolio not found
        """
        interface = 'portfolios'
        return self._operation(interface, data, 'PUT')

    def get_campaign(self, campaign_id, ads_type='sp'):
        """
        Retrieves a campaign by Id. Note that this call returns the minimal
        set of campaign fields, but is more efficient than **getCampaignEx**.

        :GET: /campaigns/{campaignId}
        :param campaign_id: The Id of the requested campaign.
        :type campaign_id: string
        :param ads_type: Type of advertisement.
        :type ads_type: string

        :returns:
            :200: Campaign
            :401: Unauthorized
            :404: Campaign not found
        """
        interface = '{}/campaigns/{}'.format(ads_type, campaign_id)
        return self._operation(interface)

    def get_campaigns(self, params=None, ads_type='sp'):
        """
        Retrieves a campaign by Id. Note that this call returns the minimal
        set of campaign fields, but is more efficient than **getCampaignEx**.

        :GET: /campaigns/{campaignId}
        :param campaign_id: The Id of the requested campaign.
        :type campaign_id: string
        :param ads_type: Type of advertisement.
        :type ads_type: string

        :returns:
            :200: Campaign
            :401: Unauthorized
            :404: Campaign not found
        """
        interface = '{}/campaigns'.format(ads_type)
        return self._operation(interface, params)

    def get_campaign_ex(self, campaign_id, ads_type='sp'):
        """
        Retrieves a campaign and its extended fields by ID. Note that this
        call returns the complete set of campaign fields (including serving
        status and other read-only fields), but is less efficient than
        **getCampaign**.

        :GET: /campaigns/extended/{campaignId}
        :param campaign_id: The Id of the requested campaign.
        :type campaign_id: string
        :param ads_type: Type of advertisement.
        :type ads_type: string

        :returns:
            :200: Campaign
            :401: Unauthorized
            :404: Campaign not found

        """
        interface = '{}/campaigns/extended/{}'.format(ads_type, campaign_id)
        return self._operation(interface)

    def create_campaigns(self, data, ads_type='sp'):
        """
        Creates one or more campaigns. Successfully created campaigns will be
        assigned unique **campaignIds**.

        :POST: /campaigns
        :param data: A list of up to 100 campaigns to be created.  Required
            fields for campaign creation are **name**, **campaignType**,
            **targetingType**, **state**, **dailyBudget** and **startDate**.
        :type data: List of **Campaign**
        :param ads_type: Type of advertisement.
        :type ads_type: string

        :returns:
            :207: List of **CampaignResponse** reflecting the same order as the
                input.
            :401: Unauthorized
        """
        interface = '{}/campaigns'.format(ads_type)
        return self._operation(interface, data, method='POST')

    def update_campaigns(self, data, ads_type='sp'):
        """
        Updates one or more campaigns.  Campaigns are identified using their
        **campaignIds**.

        :PUT: /campaigns
        :param data: A list of up to 100 updates containing **campaignIds** and
            the mutable fields to be modified. Mutable fields are **name**,
            **state**, **dailyBudget**, **startDate**, and **endDate**.
        :type data: List of **Campaign**
        :param ads_type: Type of advertisement.
        :type ads_type: string

        :returns:
            :207: List of **CampaignResponse** reflecting the same order as the
                input
            :401: Unauthorized
        """
        interface = '{}/campaigns'.format(ads_type)
        return self._operation(interface, data, method='PUT')

    def archive_campaign(self, campaign_id, ads_type='sp'):
        """
        Sets the campaign status to archived. This same operation can be
        performed via an update, but is included for completeness.

        :DELETE: /campaigns/{campaignId}
        :param campaign_id: The Id of the campaign to be archived.
        :type campaign_id: string
        :param ads_type: Type of advertisement.
        :type ads_type: string

        :returns:
            :200: Success, campaign response
            :401: Unauthorized
            :404: Campaign not found
        """
        interface = '{}/campaigns/{}'.format(ads_type, campaign_id)
        return self._operation(interface, method='DELETE')

    def list_campaigns(self, data=None, ads_type='sp'):
        """
        Retrieves a list of campaigns satisfying optional criteria.

        :GET: /campaigns
        :param ads_type: Type of advertisement.
        :type ads_type: string
        :param data: Optional, search criteria containing the following
            parameters.

        data may contain the following optional parameters:

        :param startIndex: 0-indexed record offset for the result set.
            Defaults to 0.
        :type startIndex: Integer
        :param count: Number of records to include in the paged response.
            Defaults to max page size.
        :type count: Integer
        :param campaignType: Restricts results to campaigns of a single
            campaign type. Must be **sponsoredProducts**.
        :type campaignType: String
        :param stateFilter: Restricts results to campaigns with state within
            the specified comma-separatedlist. Must be one of **enabled**,
            **paused**, **archived**. Default behavior is to include all.
        :param name: Restricts results to campaigns with the specified name.
        :type name: String
        :param campaignFilterId: Restricts results to campaigns specified in
            comma-separated list.
        :type campaignFilterId: String

        :returns:
            :200: Success. list of campaign
            :401: Unauthorized
        """
        interface = '{}/campaigns'.format(ads_type)
        return self._operation(interface, data)

    def list_campaigns_ex(self, data=None, ads_type='sp'):
        """
        Retrieves a list of campaigns with extended fields satisfying
        optional filtering criteria.

        :GET: /campaigns/extended
        :param data: Optional, search criteria containing the following
            parameters.
        :type data: JSON string
        :param ads_type: Type of advertisement.
        :type ads_type: string
        """
        interface = '{}/campaigns/extended'.format(ads_type)
        return self._operation(interface, data)

    def get_ad_group(self, ad_group_id):
        """
        Retrieves an ad group by Id. Note that this call returns the minimal
        set of ad group fields, but is more efficient than getAdGroupEx.

        :GET: /adGroups/{adGroupId}
        :param ad_group_id: The Id of the requested ad group.
        :type ad_group_id: string

        :returns:
            :200: Success, AdGroup response
            :401: Unauthorized
            :404: Ad group not found
        """
        interface = 'adGroups/{}'.format(ad_group_id)
        return self._operation(interface)

    def get_ad_group_ex(self, ad_group_id, ads_type='sp'):
        """
        Retrieves an ad group and its extended fields by ID. Note that this
        call returns the complete set of ad group fields (including serving
        status and other read-only fields), but is less efficient than
        getAdGroup.

        :GET: /adGroups/extended/{adGroupId}
        :param ad_group_id: The Id of the requested ad group.
        :type ad_group_id: string
        :param ads_type: Type of advertisement.
        :type ads_type: string

        :returns:
            :200: Success, AdGroup response
            :401: Unauthorized
            :404: Ad group not found
        """
        interface = '{}/adGroups/extended/{}'.format(ads_type, ad_group_id)
        return self._operation(interface)

    def create_ad_groups(self, data, ads_type='sp'):
        """
        Creates one or more ad groups. Successfully created ad groups will
        be assigned unique adGroupIds.

        :POST: /adGroups
        :param data: A list of up to 100 ad groups to be created. Required
            fields for ad group creation are campaignId, name, state and
            defaultBid.
        :type data: List of **AdGroup**
        :param ads_type: Type of advertisement.
        :type ads_type: string

        :returns:
            :207: Multi-status. List of AdGroupResponse reflecting the same
                order as the input
            :401: Unauthorized
        """
        interface = '{}/adGroups'.format(ads_type)
        return self._operation(interface, data, method='POST')

    def update_ad_groups(self, data, ads_type='sp'):
        """
        Updates one or more ad groups. Ad groups are identified using their
        adGroupIds.

        :PUT: /adGroups
        :param data: A list of up to 100 updates containing adGroupIds and the
            mutable fields to be modified.
        :type data: List of **AdGroup**
        :param ads_type: Type of advertisement.
        :type ads_type: string

        :returns:
            :207: Multi-status. List of AdGroupResponse reflecting the same
                order as the input
            :401: Unauthorized
        """
        interface = '{}/adGroups'.format(ads_type)
        return self._operation(interface, data, method='PUT')

    def archive_ad_group(self, ad_group_id, ads_type='sp'):
        """
        Sets the ad group status to archived. This same operation can be
        performed via an update, but is included for completeness.

        :DELETE: /adGroup/{adGroupId}
        :param ad_group_id: The Id of the ad group to be archived.
        :type ad_group_id: string
        :param ads_type: Type of advertisement.
        :type ads_type: string

        :returns:
            :200: Success. AdGroupResponse
            :401: Unauthorized
            :404: Ad group not found
        """
        interface = '{}/adGroups/{}'.format(ads_type, ad_group_id)
        return self._operation(interface, method='DELETE')

    def list_ad_groups(self, data=None, ads_type='sp'):
        """
        Retrieves a list of ad groups satisfying optional criteria.

        :GET: /adGroups
        :param ads_type: Type of advertisement.
        :type ads_type: string
        :param data: Parameter list of criteria.

        data may contain the following optional parameters:

        :param startIndex: 0-indexed record offset for the result
            set. Defaults to 0.
        :type startIndex: integer
        :param count: Number of records to include in the paged response.
            Defaults to max page size.
        :type count: integer
        :param campaignType: Restricts results to ad groups belonging to
            campaigns of the specified type. Must be sponsoredProducts
        :type campaignType: string
        :param campaignIdFilter: Restricts results to ad groups within
            campaigns specified in comma-separated list.
        :type campaignIdFilter: string
        :param adGroupIdFilter: Restricts results to ad groups specified in
            comma-separated list.
        :type adGroupIdFilter: string
        :param stateFilter: Restricts results to keywords with state within the
            specified comma-separatedlist. Must be one of enabled, paused,
            archived.  Default behavior is to include all.
        :type stateFilter: string
        :param name: Restricts results to ad groups with the specified name.
        :type name: string

        :returns:
            :200: Success. List of adGroup.
            :401: Unauthorized.

        """
        interface = '{}/adGroups'.format(ads_type)
        return self._operation(interface, data)

    def list_ad_groups_ex(self, data=None, ads_type='sp'):
        """
        Retrieves a list of ad groups satisfying optional criteria.

        :GET: /adGroups/extended
        :param ads_type: Type of advertisement.
        :type ads_type: string
        :param data: Parameter list of criteria.

        data may contain the following optional parameters:

        :param startIndex: 0-indexed record offset for the result
            set. Defaults to 0.
        :type startIndex: integer
        :param count: Number of records to include in the paged response.
            Defaults to max page size.
        :type count: integer
        :param campaignType: Restricts results to ad groups belonging to
            campaigns of the specified type. Must be sponsoredProducts
        :type campaignType: string
        :param campaignIdFilter: Restricts results to ad groups within
            campaigns specified in comma-separated list.
        :type campaignIdFilter: string
        :param adGroupIdFilter: Restricts results to ad groups specified in
            comma-separated list.
        :type adGroupIdFilter: string
        :param stateFilter: Restricts results to keywords with state within the
            specified comma-separatedlist. Must be one of enabled, paused,
            archived.  Default behavior is to include all.
        :type stateFilter: string
        :param name: Restricts results to ad groups with the specified name.
        :type name: string

        :returns:
            :200: Success. List of adGroup.
            :401: Unauthorized.
        """
        interface = '{}/adGroups/extended'.format(ads_type)
        return self._operation(interface, data)

    def get_biddable_keyword(self, keyword_id, ads_type='sp'):
        """
        Retrieves a keyword by ID. Note that this call returns the minimal set
        of keyword fields, but is more efficient than getBiddableKeywordEx.

        :GET: /keywords/{keywordId}
        :param keyword_id: The Id of the requested keyword.
        :type keyword_id: string

        :returns:
            :200: Success. Keyword.
            :401: Unauthorized.
            :404: Keyword not found.
        """
        interface = '{}/keywords/{}'.format(ads_type, keyword_id)
        return self._operation(interface)

    def get_biddable_keyword_ex(self, keyword_id, ads_type='sp'):
        """
        Retrieves a keyword and its extended fields by ID. Note that this call
        returns the complete set of keyword fields (including serving status
        and other read-only fields), but is less efficient than
        getBiddableKeyword.

        :GET: /keywords/extended/{keywordId}
        :param keyword_id: The Id of the requested keyword.
        :type keyword_id: string

        :returns:
            :200: Success. Keyword.
            :401: Unauthorized.
            :404: Keyword not found.
        """
        interface = '{}/keywords/extended/{}'.format(ads_type, keyword_id)
        return self._operation(interface)

    def create_biddable_keywords(self, data, ads_type='sp'):
        """
        Creates one or more keywords. Successfully created keywords will be
        assigned unique keywordIds.

        :POST: /keywords
        :param data: A list of up to 1000 keywords to be created. Required
            fields for keyword creation are campaignId, adGroupId, keywordText,
            matchType and state.
        :type data: List of **Keyword**
        """
        interface = '{}/keywords'.format(ads_type)
        return self._operation(interface, data, method='POST')

    def update_biddable_keywords(self, data, ads_type='sp'):
        interface = '{}/keywords'.format(ads_type)
        return self._operation(interface, data, method='PUT')

    def archive_biddable_keyword(self, keyword_id, ads_type='sp'):
        interface = '{}/keywords/{}'.format(ads_type, keyword_id)
        return self._operation(interface, method='DELETE')

    def list_biddable_keywords(self, data=None, ads_type='sp'):
        interface = '{}/keywords'.format(ads_type)
        return self._operation(interface, data)

    def list_biddable_keywords_ex(self, data=None, ads_type='sp'):
        interface = '{}/keywords/extended'.format(ads_type)
        return self._operation(interface, data)

    def get_negative_keyword(self, negative_keyword_id, ads_type='sp'):
        interface = '/negativeKeywords/{}'.format(ads_type, negative_keyword_id)
        return self._operation(interface)

    def get_negative_keyword_ex(self, negative_keyword_id, ads_type='sp'):
        interface = '/negativeKeywords/extended/{}'.format(ads_type, negative_keyword_id)
        return self._operation(interface)

    def create_negative_keywords(self, data, ads_type='sp'):
        interface = '{}/negativeKeywords'.format(ads_type)
        return self._operation(interface, data, method='POST')

    def update_negative_keywords(self, data, ads_type='sp'):
        interface = '{}/negativeKeywords'.format(ads_type)
        return self._operation(interface, data, method='PUT')

    def archive_negative_keyword(self, negative_keyword_id, ads_type='sp'):
        interface = '{}/negativeKeywords/{}'.format(ads_type, negative_keyword_id)
        return self._operation(interface, method='DELETE')

    def list_negative_keywords(self, data=None, ads_type='sp'):
        interface = '{}/negativeKeywords'.format(ads_type)
        return self._operation(interface, data)

    def list_negative_keywords_ex(self, data=None, ads_type='sp'):
        interface = '/negativeKeywords/extended'.format(ads_type)
        return self._operation(interface, data)

    def get_campaign_negative_keyword(self, campaign_negative_keyword_id, ads_type='sp'):
        interface = '{}/campaignNegativeKeywords/{}'.format(
            ads_type, campaign_negative_keyword_id)
        return self._operation(interface)

    def get_campaign_negative_keyword_ex(self, campaign_negative_keyword_id, ads_type='sp'):
        interface = '{}/campaignNegativeKeywords/extended/{}'.format(
            ads_type, campaign_negative_keyword_id)
        return self._operation(interface)

    def create_campaign_negative_keywords(self, data, ads_type='sp'):
        interface = '{}/campaignNegativeKeywords'.format(ads_type)
        return self._operation(interface, data, method='POST')

    def update_campaign_negative_keywords(self, data, ads_type='sp'):
        interface = '{}/campaignNegativeKeywords'.format(ads_type)
        return self._operation(interface, data, method='PUT')

    def remove_campaign_negative_keyword(self, campaign_negative_keyword_id, ads_type='sp'):
        interface = '{}/campaignNegativeKeywords/{}'.format(
            ads_type, campaign_negative_keyword_id)
        return self._operation(interface, method='DELETE')

    def list_campaign_negative_keywords(self, data=None, ads_type='sp'):
        interface = '{}/campaignNegativeKeywords'.format(ads_type)
        return self._operation(interface, data)

    def list_campaign_negative_keywords_ex(self, data=None, ads_type='sp'):
        interface = '{}/campaignNegativeKeywords/extended'.format(ads_type)
        return self._operation(interface, data)

    def get_suggested_keywords(self, ad_group_id, max_num_suggestions):
        params = {
            "maxNumSuggestions": max_num_suggestions
        }
        interface = 'adGroups/{}/suggested/keywords'.format(ad_group_id)
        return self._operation(interface, params)

    def get_suggested_keywords_ex(self, ad_group_id, data=None):
        """
        :param ad_group_id:
        :return:
        """
        interface = 'adGroups/{}/suggested/keywords/extended'.format(ad_group_id)
        return self._operation(interface, data)

    def get_asin_suggested_keywords(self, asin, max_num_suggestions):
        """
        :param asin:
        :return:
        """
        params = {
            "maxNumSuggestions": max_num_suggestions
        }
        interface = 'asins/{}/suggested/keywords'.format(asin)
        return self._operation(interface, params)

    def get_asin_list_suggested_keywords(self, data=None):
        """

        :param data:
        :return:
        """
        interface = 'asins/suggested/keywords'
        return self._operation(interface, data, method='POST')

    def get_adgroup_bid_recommendations(self, ad_group_id):
        """

        :param ad_group_id:
        :return:
        """

        interface = 'adGroups/{}/bidRecommendations'.format(ad_group_id)
        return self._operation(interface)

    def get_keyword_bid_recommendations(self, keyword_id):
        """

        :param keyword_id:
        :return:
        """
        interface = 'keywords/{}/bidRecommendations'.format(keyword_id)
        return self._operation(interface)

    def create_keyword_bid_recommendations(self, data=None):
        """

        :param data:
        :return:
        """
        interface = 'keywords/bidRecommendations'

        return self._operation(interface, data, method='POST')

    def get_product_ad(self, product_ad_id, ads_type='sp'):
        interface = '{}/productAds/{}'.format(ads_type, product_ad_id)
        return self._operation(interface)

    def get_product_ad_ex(self, product_ad_id, ads_type='sp'):
        interface = '{}/productAds/extended/{}'.format(ads_type, product_ad_id)
        return self._operation(interface)

    def create_product_ads(self, data, ads_type='sp'):
        interface = '{}/productAds'.format(ads_type)
        return self._operation(interface, data, method='POST')

    def update_product_ads(self, data, ads_type='sp'):
        interface = '{}/productAds'.format(ads_type)
        return self._operation(interface, data, method='PUT')

    def archive_product_ads(self, product_ad_id, ads_type='sp'):
        pass

    def list_product_ads(self, data=None, ads_type='sp'):
        interface = '{}/productAds'.format(ads_type)
        return self._operation(interface, data)

    def list_product_ads_ex(self, data=None, ads_type='sp'):
        interface = '{}/productAds/extended'.format(ads_type)
        return self._operation(interface, data)

    def create_targeting_clauses(self, data=None):
        interface = 'sp/targets'
        return self._operation(interface, data, method='POST')

    def update_targeting_clauses(self, data=None):
        interface = 'sp/targets'
        return self._operation(interface, data, method='PUT')

    def list_target_recommendations(self, data=None):
        """
        Generate list of recommended products to target, based on the ASIN that is input. Successful response will be a list of recommended ASINs to target.
        """
        interface = 'sp/targets/productRecommendations'
        return self._operation(interface, data, method='POST')

    def list_targeting_categories(self, data=None):
        """
        Get list of targeting categories.
        """
        interface = 'sp/targets/categories'
        return self._operation(interface, data)

    def request_snapshot(self, record_type=None, snapshot_id=None, data=None):
        if record_type is not None:
            interface = '{}/snapshot'.format(record_type)
            return self._operation(interface, data, method='POST')
        elif snapshot_id is not None:
            interface = 'snapshots/{}'.format(snapshot_id)
            return self._operation(interface, data)

    def request_report(self, record_type=None, report_id=None, data=None, ads_type='sp'):
        if record_type is not None:
            interface = '{}/{}/report'.format(ads_type, record_type)
            return self._operation(interface, data, method='POST')
        elif report_id is not None:
            interface = 'reports/{}'.format(report_id)
            return self._operation(interface)

    def get_report(self, report_id):
        interface = 'reports/{}'.format(report_id)
        res = self._operation(interface)
        if res['response']['status'] == 'SUCCESS':
            res = self._download(
                location=res['response']['location'])
            return res
        else:
            return res

    def get_snapshot(self, snapshot_id):
        interface = 'snapshots/{}'.format(snapshot_id)
        res = self._operation(interface)
        if json.loads(res['response'])['status'] == 'SUCCESS':
            res = self._download(
                location=json.loads(res['response'])['location'])
            return res
        else:
            return res

    def _download(self, location):
        headers = {'Authorization': 'Bearer {}'.format(self._access_token),
                   'Content-Type': 'application/json',
                   'User-Agent': self.user_agent,
                   'Amazon-Advertising-API-ClientId': self.client_id}

        if self.profile_id is not None:
            headers['Amazon-Advertising-API-Scope'] = self.profile_id
        else:
            raise ValueError('Invalid profile Id.')

        opener = urllib.request.build_opener(NoRedirectHandler())
        urllib.request.install_opener(opener)
        req = urllib.request.Request(url=location, headers=headers, data=None)
        try:
            response = urllib.request.urlopen(req)
            if 'location' in response:
                if response['location'] is not None:
                    req = urllib.request.Request(url=response['location'])
                    res = urllib.request.urlopen(req)
                    res_data = res.read()

                    buf = BytesIO(res_data)
                    f = gzip.GzipFile(fileobj=buf)
                    data = f.read()
                    return {'success': True,
                            'code': res.code,
                            'response': {'status': 'SUCCESS',
                                         'data': json.loads(data.decode('utf-8'))
                                         }
                            }
                else:
                    return {'success': False,
                            'code': res.code,
                            'response': {'status': 'FAIL',
                                         'statusDetails': 'Location is empty.'
                                         }
                            }
            else:
                return {'success': False,
                        'code': res.code,
                        'response': {'status': 'FAIL',
                                     'statusDetails': 'Location not found.'
                                     }
                        }
        except urllib.error.HTTPError as e:
            return {'success': False,
                    'code': e.code,
                    'response': e.msg}

    def _operation(self, interface, params=None, method='GET', auto_refresh=True):
        """
        Makes that actual API call.

        :param interface: Interface used for this call.
        :type interface: string
        :param params: Parameters associated with this call.
        :type params: GET: string POST: dictionary
        :param method: Call method. Should be either 'GET' or 'POST'
        :type method: string
        """
        if self._access_token is None:  # get access_token from refresh_token.
            result = self.do_refresh_token()
            if result["success"] is False:
                return {'success': False,
                        'code': 0,
                        'response': 'access_token is empty.'}

        headers = {'Authorization': 'bearer {}'.format(self._access_token),
                   'Content-Type': 'application/json',
                   'User-Agent': self.user_agent,
                   'Amazon-Advertising-API-ClientId': self.client_id}

        if self.profile_id is not None and self.profile_id != '':
            headers['Amazon-Advertising-API-Scope'] = self.profile_id

        data = None

        if method == 'GET':
            if params is not None:
                p = '?{}'.format(urllib.parse.urlencode(params))
            else:
                p = ''

            url = 'https://{host}/{api_version}/{interface}{params}'.format(
                host=self.endpoint,
                api_version=self.api_version,
                interface=interface,
                params=p)
        else:
            if params is not None:
                data = json.dumps(params).encode('utf-8')

            url = 'https://{host}/{api_version}/{interface}'.format(
                host=self.endpoint,
                api_version=self.api_version,
                interface=interface)

        req = urllib.request.Request(url=url, headers=headers, data=data)
        req.method = method

        try:
            f = urllib.request.urlopen(req)
            return {'success': True,
                    'code': f.code,
                    'response': json.loads(f.read().decode('utf-8'))}
        except urllib.error.HTTPError as e:
            detail = json.loads(e.read().decode('utf-8'))["details"]
            if e.code == 401 and detail == "Authentication failed" and auto_refresh:
                self.do_refresh_token()
                return self._operation(interface, params, method, False)
            else:
                return {'success': False,
                        'code': e.code,
                        'response': e.msg,
                        'detail': detail
                        }


class NoRedirectHandler(urllib.request.HTTPErrorProcessor):
    """Handles report and snapshot redirects."""

    def http_response(self, request, response):
        if response.code == 307:
            if 'Location' in response.headers:
                return {'code': 307,
                        'location': response.headers['Location']}
            else:
                return {'code': response.code, 'location': None}
        else:
            return urllib.request.HTTPErrorProcessor.http_response(
                self, request, response)

    https_response = http_response
