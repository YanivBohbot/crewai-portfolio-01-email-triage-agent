#!/usr/bin/env python
import os
import sys

from pydantic import BaseModel, Field

from crewai import Agent
from crewai.flow import Flow, start
from crewai.mcp import MCPServerStdio


class EmailClassification(BaseModel):
    email_id: str = Field(description="l'id exact renvoyé par le tool, ex: 'msg_001' — copié tel quel, jamais reformulé")
    sender: str
    priority: str = Field(description="urgent, normal ou spam")
    summary: str = Field(description="résumé en une phrase")
    suggested_action: str = Field(description="action recommandée, jamais 'envoyer' ou 'supprimer'")


class TriageReport(BaseModel):
    emails: list[EmailClassification]


class TriageState(BaseModel):
    report: TriageReport | None = None


class EmailTriageFlow(Flow[TriageState]):

    @start()
    def triage_inbox(self):
        gmail_mcp = MCPServerStdio(
            command=sys.executable,
            args=["-m", "email_triage.mcp_servers.gmail_mock_server"],
        )

        triage_agent = Agent(
            role="Email Triage Specialist",
            goal="Lire les emails récents et les classer par priorité, sans jamais répondre ni supprimer",
            backstory=(
                "Assistant prudent et méthodique. Ne fait que lire et classer : "
                "liste les emails récents puis récupère le détail de chacun avant de juger la priorité."
            ),
            mcps=[gmail_mcp],
            llm=os.environ.get("MODEL", "openai/gpt-4.1-mini"),
            verbose=True,
        )

        result = triage_agent.kickoff(
            "Liste les emails récents de la boîte, récupère le détail de chacun, "
            "puis classe-les par priorité (urgent, normal, spam) avec un résumé "
            "et une action suggérée pour chacun. Important: email_id doit être "
            "copié exactement depuis le champ 'id' renvoyé par les tools (ex: 'msg_001'), "
            "jamais reformulé ou deviné.",
            response_format=TriageReport,
        )

        self.state.report = result.pydantic


def kickoff():
    flow = EmailTriageFlow()
    flow.kickoff()

    print("\n=== RAPPORT DE TRIAGE ===")
    for email in flow.state.report.emails:
        print(f"[{email.priority.upper():6}] {email.sender} — {email.summary}")
        print(f"         → {email.suggested_action}\n")


def plot():
    flow = EmailTriageFlow()
    flow.plot()


if __name__ == "__main__":
    kickoff()
