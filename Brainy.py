import os
import sys
import urllib
import urllib2
import json
import random
from itty import *
from pymongo import MongoClient
from spark import Spark
from settings import Settings

client = MongoClient("localhost", 27017)
db = client.brainy_mongo_db

class Quiz_facts(object):

    def __init__(self):
        self = None

    def quiz_send_to_db(self, roomId, question, answer, choices):
        
        db.quiz.remove({'RoomId': roomId})
        db.quiz.insert({"RoomId": roomId, "Question" : question, "Answer": answer})
        
        db.choices.remove({'RoomId': roomId})
        db.choices.insert({"RoomId": roomId, "Choices": choices})


    def quiz_retrieve_answer_db(self, roomId):
        
        db.quiz.find_one({"RoomId":roomId})
        answer = db.quiz.find_one({"RoomId":roomId})["Answer"]
        print answer
        return answer


    def quiz_retrieve_choices_db(self, roomId):
        
        db.choices.find_one({"RoomId":roomId})
        choices = db.choices.find_one({"RoomId":roomId})["Choices"]
        print choices
        return choices
        

    def quiz_questions(self):

        url = "https://opentdb.com/api.php?amount=1"
        request = urllib2.Request(url,headers={"Accept" : "application/json","Content-Type":"application/json"})
        contents = urllib2.urlopen(request).read()
        contents = json.loads(contents)
        if len(contents["results"]) > 0:

            results = contents["results"][0]
            print results
            type = results["type"]
            question = results["question"]
            correct_answer = results["correct_answer"]
            wrong_answer = results["incorrect_answers"]

            #print type
            #print question
            #print correct_answer
            #print wrong_answer
            return type, question, correct_answer, wrong_answer
        else:
            return None


    def numbersapi_facts(self,in_message):

        in_message = in_message.strip()
        url = "http://numbersapi.com/random/{0}".format(in_message)
        request = urllib2.Request(url,headers={"Accept" : "application/json","Content-Type":"application/json"})
        contents = urllib2.urlopen(request).read()
        contents = json.loads(contents)
        fact = contents["text"]
        return fact


    def quiz(self, roomId):
        type, question, correct_answer, wrong_answer = self.quiz_questions()
        if type != None and question != None and correct_answer != None and wrong_answer != None:
            print question
            print correct_answer
            print wrong_answer
            #choices = correct_answer + wrong_answer
            choices = wrong_answer + [correct_answer]
            #print choices

            if type == "boolean":
                #quiz_send_to_db(question, choices = 0)
                self.quiz_send_to_db(roomId,question, correct_answer, choices = [0])


                msg = question+"\n\n"+"<br/>"
                msg +="Tag me with **True** or **False** to answer or **Pass** to skip this question."
                return msg


            else:
                
                choices = random.sample(choices, len(choices))
                print choices
                #quiz_send_to_db(question, choices)
                self.quiz_send_to_db(roomId, question, correct_answer, choices)
                i = 1
                msg_1 = ""
                for choice in choices:
                    i += i
                    msg_1 +="{0}. {1}\n\n".format(i, choice)
                    msg = question+"\n\n"+"\n\n" + msg_1
                    msg += "**Choose one of the numbers to answer or type Pass to skip this question.**\n\n"
                    msg += "eg: **Brainy** 3, **Brainy** pass\n\n"
                return msg
        else:
            msg = "Sorry, no question found. Try again"
            return msg


    def help_msg(self):
        msg ="Hi! Are you ready to have some fun?\n\n"
        msg += "There are two sections you can choose from: **Quiz** and **Facts**. \n\n"
        msg += "* **Brainy** quiz, to take up the challenge.\n\n"
        msg += "For **Facts** you can choose from categories: **trivia**, **year**, **date** or **math**, so for example simply tag this bot as follows:\n\n"
        msg += "* **Brainy** math\n\n"
        return msg



@post('/')
def index(request):
    """
    Processes webhook payload
    """
    try:

        print request.body
        webhook = json.loads(request.body)
        requester = webhook['data']['personEmail']
        roomId = webhook['data']['roomId']
        facts = ["trivia", "year", "math", "date"]
        if requester != bot_email:
            result = spar.get('https://api.ciscospark.com/v1/messages/{0}'.format(webhook['data']['id']))
            in_message = result.contents.get('text', '').lower()
            in_message = in_message.replace(bot_name, "").strip()
            print in_message
            msg = None
            if "quiz" in in_message:
                in_message = in_message.replace("quiz", "").strip()
                msg = game.quiz(roomId)

            elif "pass" in in_message:
                msg = game.quiz(roomId)

            elif any(fact in in_message for fact in facts):
                msg = game.numbersapi_facts(in_message)

            elif "help" in in_message:
                msg = game.help_msg()

            else:
                in_message = in_message.strip()
                correct_answer = game.quiz_retrieve_answer_db(roomId)
                choices = game.quiz_retrieve_choices_db(roomId)
                #print choices
                try:

                    val = int(in_message)
                    if 0 < val <= len(choices):

                        user_choice = choices[val-1]
                        print "Users Choice:", user_choice
                        if user_choice.lower() == correct_answer.lower():
                            msg = "Good job!"
                        else:
                            msg = "Wrong answer. The correct answer is: {0}".format(correct_answer)
                    else:
                        msg = "Your choice doesn't exist, try again."

                except ValueError:

                    ans = ["true", "false"]

                    if any(ans in in_message for ans in ans):
                        if in_message == correct_answer.lower():
                            msg = "Good job!"
                        else:
                            msg = "Wrong answer. The correct answer is: {0}".format(correct_answer)
                    else:

                        msg = "Wrong input"

            if msg != None:
                spar.post('https://api.ciscospark.com/v1/messages', {'markdown':msg, 'roomId':webhook['data']['roomId']})
        return "true"

    except urllib2.HTTPError as e:
        print("Error_Code: ", e.code, "Reason: ", e.reason)
        msg = "Oops, something went wrong with the server. Please try again"
        spar.post('https://api.ciscospark.com/v1/messages', {'markdown':msg, 'roomId':webhook['data']['roomId']})


if __name__ == "__main__":
    bot_email = "BOT_EMAIL"
    bot_name = "BOT_NAME"
    spar = Spark(Settings.token)
    game = Quiz_facts()
    run_itty(server='wsgiref', host='0.0.0.0', port=10070)
