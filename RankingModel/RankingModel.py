# using support vector regression: features -> ranking score
from sklearn import svm
# ranking
from collections import Counter
from ModelBase import ModelBase

class RankingModel(ModelBase):
    def __init__(self, extract_features, all_algos, num_neg=1, limit_features=None):
        super(RankingModel, self).__init__(extract_features, all_algos, num_neg, limit_features)
        self.model = None

    def clone(self):
        return RankingModel(self._extract_features, self.all_algos,
            self.num_neg, self.limit_features)

    def _train_ranking(self, feature_vector, score_vector):
        clf = svm.LinearSVR()
        # train
        clf.fit(feature_vector, score_vector)
        self.model = clf

    def train(self, data):
        (feature_vector, score_vector) = self._create_training_vectors(data)
        # first train ranking model
        self._train_ranking(feature_vector, score_vector)

    def _classify_rank(self, sample, candidates):
        ranks = Counter()

        for cand in candidates:
            sample_features = self._get_feature_vector(sample, cand)
            [result] = self.model.predict([sample_features])
            ranks[cand] = result
        return ranks.most_common()

    def classify(self, sample, candidates=None):
        candidates = candidates or self.all_algos
        results = self._classify_rank(sample, candidates)
        (topcand, toprank) = results[0]
        return (topcand, results)

    @staticmethod
    def init_results():
        return {
            'recranks': [],
            'correct|inset': []
        }

    def eval(self, sample, prediction, results):
        (guess, result) = prediction

        if sample.label is not None and sample.is_algo:
            keys = zip(*result)[0]
            print "Top Rank:", result[0:3]
            rank = keys.index(sample.label) + 1
            print "Rank of Correct Algo:", rank
            results['recranks'].append(1.0 / rank)
            results['correct|inset'].append(sample.label == guess)

    def print_model(self):
        print "Coef: ", self.rankingModel.coef_
        print "Threshold: ", self.thresholdModel.tree_