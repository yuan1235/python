# -*- coding: utf-8 -*-
# writer : lgy
# data : 2017-09-08

# function  解决HDA 的话题分析数据处理以及数据矩阵构建

import sys

sys.path.append('../..')
reload(sys)
import pickle
from MyCode import config
import logging
import gensim
import jieba

logging.basicConfig(filename='logger.log', format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


class HDA(object):
	def __init__(self, modelName="HDATopicWord_1000", word_dic_name="Hda_id2word_1000"):
		self.modelname = modelName
		self.word_dic_name = word_dic_name
		self.HDA_model = None
		self.word_dic = None
		self.topics = None

	def build_word_dic(self, documents):
		print "build word dic"
		self.word_dic = gensim.corpora.Dictionary(documents=documents)
		# print len(self.word_dic)
		print "build finished and write dic to file"
		with open(config.ModelPath + self.word_dic_name + ".model", 'wb') as fp:
			pickle.dump(self.word_dic, fp)
		logging.info("build word dic finished and write dic to file")

	def buildModel(self, documents):
		modelfile = config.ModelPath + self.modelname + ".model"
		print "Train HDA Model ... ..."
		logging.info("构建词典")
		self.build_word_dic(documents)
		logging.info("训练模型")
		trainCorpus = [self.word_dic.doc2bow(docment) for docment in documents]
		tfidf = gensim.models.TfidfModel(trainCorpus)
		corpustfidf = tfidf[trainCorpus]
		self.HDA_model = gensim.models.HdpModel(corpustfidf, id2word=self.word_dic,T=1000)
		logging.info("存储模型{0}".format(self.modelname))
		print "Finished Train HDA Model and saving ... ..."
		with open(modelfile, "wb") as model_fp:
			pickle.dump(self.HDA_model, model_fp)
		print "Finished save HDA Model"
		logging.info("build HDA model finished and write dic to file")

	def load_word_dic(self):
		word_dic_file = config.ModelPath + self.word_dic_name + ".model"
		try:
			if self.word_dic:
				return self.word_dic
			logging.info("load word dic ")
			print "load word dic ... ..."
			with open(word_dic_file, "rb") as fp:
				self.word_dic = pickle.load(fp)
			print "load success"
		except:
			print "word dic not found !"
			return None

	def load_HDAModel(self):
		ladmodel_file = config.ModelPath + self.modelname + ".model"
		try:
			if self.HDA_model:
				return self.HDA_model
			logging.info("load HDA Model ")
			print "load HDA Model ... ..."
			with open(ladmodel_file, "rb") as fp:
				self.HDA_model = pickle.load(fp)
			print "load success"
		except:
			print "HDA Model not found !"
			return None

		# # 处理语句成query
		# def getQueries(sentences):
		# 	par_sentences = Participle.Participle(sentences)
		# 	# thl = thulac.thulac()
		# 	# par_sentences = [thl.cut(sen.encode("utf-8")) for sen in sentences]
		# 	# documents = filterStopWords.filterStopWordFromSentences(par_sentences)
		# 	documents = par_sentences
		# 	return documents

	def getWordsId(self, document):
		documentId = self.word_dic.doc2bow(document)
		return documentId

	def getQuery(self, sentence):
		par_sentences = jieba.cut(sentence.strip())
		documents = par_sentences
		return documents

	# 处理query 的话题
	def getQuerySimilarly(self, query, top_n=3):
		logging.info("计算文档集的话题")
		sentence = list(jieba.cut(query))
		# print sentence
		sentence_id = self.word_dic.doc2bow(sentence)
		doc_topic = self.HDA_model[sentence_id][:top_n]
		doc_topic = sorted(doc_topic, key=lambda X: X[1], reverse=True)[:top_n]
		return doc_topic

	def getTopicLab(self,sentence):
		if sentence is None or sentence == '':
			return None, None
		doc_topic = self.getQuerySimilarly(sentence)
		if doc_topic == None or len(doc_topic) == 0:
			return None, None
		for topic in doc_topic:
			return topic[0], topic[1]

	def show(self):
		self.HDA_model.show_topics(num_topics=10,num_words=10)