_agents = {}


def register(name, agent):
    _agents[name] = agent


def get(name):
    return _agents.get(name)


def list_agents():
    return list(_agents.keys())


from Agents.Translator.translator import Translator
from Agents.Programmer.programmer import Programmer
from Agents.Planner.planner import Planner
from Agents.Literature.literature import LiteratureAgent
from Agents.Writer.writer import WriterAgent
from Agents.Researcher.researcher import Researcher
from Agents.Ranking.ranking import RankingAgent
from Agents.Summarizer.summarizer import Summarizer
from Agents.Cluster.cluster_agent import ClusterAgent
from Agents.Outline.outline_agent import OutlineAgent
from Agents.Reviewer.reviewer import Reviewer


register("Translator", Translator())
register("Programmer", Programmer())
register("Planner", Planner())
register("Literature", LiteratureAgent())
register("Writer", WriterAgent())
register("Researcher", Researcher())
register("Ranking", RankingAgent())
register("Summarizer", Summarizer())
register("Cluster", ClusterAgent())
register("Outline", OutlineAgent())
register("Reviewer", Reviewer())