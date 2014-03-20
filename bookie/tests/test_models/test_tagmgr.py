"""Test the basics including the bmark and tags"""
from pyramid import testing
from topia.termextract import extract
from bookie.models import DBSession
from bookie.models import Tag
from bookie.models import TagMgr

from bookie.tests import empty_db
from bookie.tests import gen_random_word
from bookie.tests import TestDBBase
from bookie.tests.factory import make_tag


class TestTagMgrStats(TestDBBase):
    """Handle some TagMgr stats checks"""

    def setUp(self):
        """Setup Tests"""
        from pyramid.paster import get_app
        from bookie.tests import BOOKIE_TEST_INI
        app = get_app(BOOKIE_TEST_INI, 'bookie')
        from webtest import TestApp
        self.testapp = TestApp(app)
        testing.setUp()

    def tearDown(self):
        """Tear down each test"""
        testing.tearDown()
        empty_db()

    def test_total_ct(self):
        """Verify that our total count method is working"""
        ct = 5
        for i in range(ct):
            t = Tag(gen_random_word(10))
            DBSession.add(t)

        ct = TagMgr.count()
        self.assertEqual(5, ct, 'We should have a total of 5: ' + str(ct))

    def test_basic_complete(self):
        """Tags should provide completion options."""
        # Generate demo tag into the system
        tags = [make_tag() for i in range(5)]
        [DBSession.add(t) for t in tags]

        test_str = tags[0].name[0:2]
        suggestions = TagMgr.complete(test_str)

        self.assertTrue(
            tags[0] in suggestions,
            "The sample tag was found in the completion set")

    def test_case_insensitive(self):
        """Suggestion does not care about case of the prefix."""
        # Generate demo tag into the system
        tags = [make_tag() for i in range(5)]
        [DBSession.add(t) for t in tags]

        test_str = tags[0].name[0:4].upper()
        suggestions = TagMgr.complete(test_str)
        self.assertTrue(
            tags[0] in suggestions,
            "The sample tag was found in the completion set")
    def test_suggested_tags(self):        
        """Suggestions based on the content of the bookmarked page"""
        # login into bookie
        user_data = {'login': u'admin',
                     'password': u'admin',
                     'form.submitted': u'true'}
        
        res = self.testapp.post('/login',
                                params=user_data)
        
        # Add a boookmark
        res = DBSession.execute(
            "SELECT api_key FROM users WHERE username = 'admin'").fetchone()
        key = res['api_key']
        url = u'http://bmark.us'
        test_bmark = {
            'url': url,
            'description': u'Bookie',
            'extended': u'',
            'tags': u'',
            'api_key': key,
        }
        
        res = self.testapp.post('/api/v1/admin/bmark',
                                params=test_bmark,
                                status=200)
        
        # generate tags for the bookmark
        tag_suggest = []
        bmark = BmarkMgr.get_by_url(url)    
        hash_id = bmark.hash_id
        # If bmark is not parsed return empty tag list
        if bmark.readable.status_code == '900':
           # Do Nothing
        else:
            content = bmark.readable.content
            # Remove unicode character while printing
            clean_content = ("".join(BeautifulSoup(content).findAll(text=True)).encode('ascii','ignore'))                     
            get_tags = extract.TermExtractor()
            tag_suggest = TagMgr.sort_word_strength(get_tags(clean_content))
            tag_list = []
            for tag in tag_suggest:
                tag_list.append((tag[0]))
                tag_list = list(set(tag_list))
                # only maximum of 5 tags
            if len(tag_list) >= 5:
                tag_list = tag_list[0:5]
        edit_bmark = {
        'hash_id': hash_id,
        'username': 'admin',
        'url': url,
        }    
        res = self.testapp.post('/admin/edit/'+hash_id,
                                params=edit_bmark,
                                status=200)    
        for tag in tag_list:
        	self.assertIn(tag, res.body)            
