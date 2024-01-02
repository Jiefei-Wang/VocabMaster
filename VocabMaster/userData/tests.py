from typing import Any
from django.test import TestCase
from VocabMaster.userData.models import *


# Test GlossaryBooks
class GlossaryBooksTestCase(TestCase):
    userName = "test_case"
    bookName = "book1"

    alterUserNames = ["test_case2", "test_case3", "test_case4"]
    alterBookNames = ["book2", "book3", "book4"]
    def setUp(self):
        pass
        
    def testGlossaryBook(self):
        ## add and exists methods
        GlossaryBooks.add(self.userName, self.bookName)
        self.assertTrue(GlossaryBooks.exists(self.userName, self.bookName))

        ## add alternatives
        for i in range(len(self.alterUserNames)):
            for j in range(len(self.alterBookNames)):
                GlossaryBooks.add(self.alterUserNames[i], self.alterBookNames[j])
        
        ## get method
        objs = GlossaryBooks.filter(self.userName, self.bookName)
        self.assertEqual(len(objs),1)
        obj = objs[0]
        self.assertEqual(obj.user, self.userName)
        self.assertEqual(obj.bookName, self.bookName)

        ## get method 2
        objs = GlossaryBooks.filter(self.userName)
        self.assertEqual(len(objs),1)

        ## delete method
        GlossaryBooks.delete(self.userName, self.bookName)
        self.assertFalse(GlossaryBooks.exists(self.userName, self.bookName))

        ## delete non-exist book. No error should be raised.
        GlossaryBooks.delete(self.userName, self.bookName)

        ## detele all books
        for i in range(len(self.alterUserNames)):
            for j in range(len(self.alterBookNames)):
                GlossaryBooks.delete(self.alterUserNames[i], self.alterBookNames[j])


class GlossaryWordsTestCase(TestCase):
    userName = "test_case"
    bookName = "book1"
    word = "word1"

    alterUserNames = ["test_case2", "test_case3", "test_case4"]
    alterBookNames = ["book2", "book3", "book4"]
    alterWords = ["word2", "word3", "word4"]
    def testGlossaryWords(self):
        GlossaryBooks.add(self.userName, self.bookName)
        ## add and exists methods
        GlossaryWords.add(self.userName, self.bookName, self.word)
        self.assertTrue(GlossaryWords.exists(self.userName, self.bookName, self.word))

        ## add alternatives books
        for i in range(len(self.alterUserNames)):
            for j in range(len(self.alterBookNames)):
                GlossaryBooks.add(self.alterUserNames[i], self.alterBookNames[j])
                
        ## add alternatives
        for i in range(len(self.alterUserNames)):
            for j in range(len(self.alterBookNames)):
                for k in range(len(self.alterWords)):
                    GlossaryWords.add(self.alterUserNames[i], self.alterBookNames[j], self.alterWords[k])

        ## get method
        objs = GlossaryWords.filter(self.userName, self.bookName)
        self.assertEqual(len(objs),1)
        obj = objs[0]
        self.assertEqual(obj.book.user, self.userName)
        self.assertEqual(obj.book.bookName, self.bookName)
        self.assertEqual(obj.word, self.word)

        ## delete method
        GlossaryWords.delete(self.userName, self.bookName, self.word)
        self.assertFalse(GlossaryWords.exists(self.userName, self.bookName, self.word))
        GlossaryBooks.delete(self.userName, self.bookName)

        ## get non-exist word
        self.assertRaises(Exception, GlossaryWords.filter, self.userName, self.bookName)

        ## delete non-exist word
        self.assertRaises(Exception, GlossaryWords.delete, self.userName, self.bookName, self.word)

        ## detele all words by deleting books
        for i in range(len(self.alterUserNames)):
            for j in range(len(self.alterBookNames)):
                GlossaryBooks.delete(self.alterUserNames[i], self.alterBookNames[j])



def testUserDefined(testClass, testObj):
    userName = "test_case"
    word = "word1"
    meaning = "meaning1"

    alterUserNames = ["test_case2", "test_case3", "test_case4"]
    alterWords = ["word2", "word3", "word4"]
    alterMeanings = ["meaning2", "meaning3", "meaning4"]

    ## add and exists methods
    testObj.assertFalse(testClass.exists(userName, word))
    testClass.add(userName, word, meaning)
    testObj.assertTrue(testClass.exists(userName, word))

    ## add alternatives
    for i in range(len(alterUserNames)):
        for j in range(len(alterWords)):
                testClass.add(alterUserNames[i], alterWords[j], alterMeanings[j])
    
    ## get method
    objs = testClass.filter(userName, word)
    testObj.assertEqual(len(objs),1)
    obj = objs[0]
    testObj.assertEqual(obj.user, userName)
    testObj.assertEqual(word, word)
    testObj.assertEqual(meaning, meaning)

    ## get method 2
    objs = testClass.filter(userName)
    testObj.assertEqual(len(objs),1)

    ## delete method
    testClass.delete(userName, word)
    testObj.assertFalse(testClass.exists(userName, word))

    ## get non-exist word
    objs = testClass.filter(userName, word)
    testObj.assertEqual(len(objs),0)

    ## get non-exist word 2
    objs = testClass.filter(userName)
    testObj.assertEqual(len(objs),0)

    ## detele all words
    for i in range(len(alterUserNames)):
        for j in range(len(alterWords)):
            testClass.delete(alterUserNames[i], alterWords[j])


class UserDefinedWordMeaningTestCase(TestCase):
    def testUserDefinedWordMeaning(self):
        testUserDefined(UserDefinedWordMeaning,self)

class UserDefinedWordNoteTestCase(TestCase):
    def testUserDefinedWordMeaning(self):
        testUserDefined(UserDefinedWordNote,self)

class HistoryTestCase(TestCase):
    def testHistory(self):
        userName = "test_case"
        word1 = "word1"
        uuid1= "uuid1"
        bookName1 = "book1"
        answer = 1
        
        word2 = "word2"
        uuid2= "uuid2"
        bookName2 = "book2"
        answer2 = 2

        ## add and exists methods
        self.assertFalse(History.exists(userName, word1))
        History.add(userName, uuid1, word1, bookName1, answer)
        self.assertTrue(History.exists(userName, word1))

        ## add alternatives
        History.add(userName, uuid2, word2, bookName2, answer2)

        ## get method
        objs = History.filter(userName, word1)
        self.assertEqual(len(objs),1)
        obj = objs[0]
        self.assertEqual(obj.user, userName)
        self.assertEqual(obj.word, word1)
        self.assertEqual(obj.uuid, uuid1)
        self.assertEqual(obj.bookName, bookName1)
        self.assertEqual(obj.answer, answer)

        ## get method 2
        objs = History.filter(userName)
        self.assertEqual(len(objs),2)

        ## delete method
        History.delete(userName, word1)
        self.assertFalse(History.exists(userName, word1))

        ## get all words
        objs = History.filter(userName)
        self.assertEqual(len(objs),1)


class UserInfoTestCase(TestCase):

    def testUserInfo(self):
        userNames = ["test_case", "test_case2", "test_case3", "test_case4"]
        glossaryBooks = ["book1", "book2", "book3", "book4"]

        ## add and exists methods
        self.assertFalse(UserInfo.exists(userNames[0]))
        template = UserInfo.getTemplate()
        for i in range(len(userNames)):
            template['glossaryBook'] = glossaryBooks[i]
            UserInfo.add(userNames[i], template)
        self.assertTrue(UserInfo.exists(userNames[0]))

        ## get method
        obj = UserInfo.get(userNames[0])
        self.assertEqual(obj.user, userNames[0])
        self.assertEqual(obj.glossaryBook, glossaryBooks[0])

        ## update method
        UserInfo.update(userNames[0], {'glossaryBook': 'test'})
        obj = UserInfo.get(userNames[0])
        self.assertEqual(obj.glossaryBook, 'test')

        ## delete method
        UserInfo.delete(userNames[0])
        self.assertFalse(UserInfo.exists(userNames[0]))

        ## get non-exist user
        self.assertRaises(Exception, UserInfo.get, userNames[0])

        ## detele all users
        for i in range(len(userNames)):
            UserInfo.delete(userNames[i])



