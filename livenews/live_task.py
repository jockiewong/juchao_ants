from livenews.merge_spider import MergeJuchaoDayNews
from livenews.single_spider import SingleJuchaoDayNews


def main():
    MergeJuchaoDayNews().run()
    SingleJuchaoDayNews().start()
