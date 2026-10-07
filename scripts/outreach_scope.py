#!/usr/bin/env python3
"""Who would right-of-reply outreach actually go to, and who should it skip?

Written 2026-10-07. The outreach ask has been open two days as a general
proposal ("contact the subjects"). That is not a plan - it is a sentence.
Before Carolina can give a meaningful yes or no, she needs to see the actual
list, including the ones I would NOT contact and why.

Classifies all 22 entries. Prints the list a yes would authorise.

    /usr/bin/python3 scripts/outreach_scope.py
"""
import sys

# (entry, subject, contactable, reason)
# contactable: "yes" / "no" / "n-a"
SUBJECTS = [
    (1, "AgentMint", "no",
     "No named operator found; the site's /about, /methodology and /faq all "
     "404. There is nobody identifiable to write to."),
    (2, "AgentMRR", "yes",
     "Operator is identifiable and runs a public leaderboard with a "
     "submission process."),
    (3, "x402", "no",
     "A protocol with institutional backing (Linux Foundation, Coinbase, "
     "Cloudflare). The entry faults third-party citation, not the protocol. "
     "No single party to notify."),
    (4, "Bottleneck Labs (first pass)", "yes",
     "Published research with a named lab. Same subject as entry 10 - ONE "
     "message covering both, not two."),
    (5, "hermes-advisor-skill", "no",
     "The entry's finding is about a Reddit headline that rounded the "
     "author's own accurate figures up. The claimant did nothing wrong; "
     "contacting them implies otherwise."),
    (6, "venturebot (this agent)", "n-a", "That is me."),
    (7, "Token-based agent revenue leaderboards", "no",
     "A category, not a party. Entry 15 covers the named protocols."),
    (8, "Automaton", "yes",
     "Named creator with a public repo. The entry is exculpatory toward him - "
     "the inflation was entirely third-party - which is worth him knowing."),
    (9, "OpenClaw / getdavid.ai", "yes",
     "Named operator, public podcast appearance, public company."),
    (10, "Bottleneck Labs (second pass)", "no",
     "Duplicate subject - covered by the entry 4 message."),
    (11, "Felix / Nat Eliason", "yes",
     "Named operator with a public dashboard and a published breakdown."),
    (12, "BugBasher / Sandra Yang / Ramp", "yes",
     "Named engineer at a named company who published the result herself. "
     "The entry credits her honesty; the milestone-framing criticism is "
     "aimed at coverage, not at her."),
    (13, "Lancer / Ivan Nedelkovski", "yes",
     "Named founder, verdict Corroborated, TrustMRR-verified."),
    (14, "SEObot / John Rush", "yes",
     "Named founder. The entry is adverse on framing - he has the strongest "
     "claim on a reply of anyone here."),
    (15, "Virtuals + Clanker", "no",
     "Protocols with diffuse governance; the entry's finding is about what "
     "leaderboards display, not a company's own claim."),
    (16, "ProspectZero / Matt Anderson", "yes",
     "Named founder. Verdict withheld - the finding is about the trackers, "
     "not about him, which he should know."),
    (17, "Hans Kraemer / dfdx labs", "yes",
     "Named lab with a published research page."),
    (18, "Agent-economy market forecasts", "no",
     "The entry audits citation practice across MarketsandMarkets, Grand "
     "View, Gartner, McKinsey and several outlets. No single party is the "
     "subject, and TNW is credited positively."),
    (19, "Cognition / Devin", "yes",
     "Named company. The entry's criticism is of coverage, not of their "
     "announcement, which is worth saying directly."),
    (20, "Genspark", "yes",
     "Named company. The finding is source concentration in coverage; the "
     "company confirmed only the $100M figure."),
    (21, "Sierra", "yes",
     "Named company. The entry's finding is a label drift in press coverage, "
     "and all three of their milestones are company-confirmed."),
    (22, "AI Hustler / Marcin Dudek", "yes",
     "Named operator who published his own failures in detail. Verdict "
     "Corroborated."),
]


def main():
    yes = [s for s in SUBJECTS if s[2] == "yes"]
    no = [s for s in SUBJECTS if s[2] == "no"]
    na = [s for s in SUBJECTS if s[2] == "n-a"]

    print(f"=== WOULD CONTACT: {len(yes)} ===")
    for n, subj, _, why in yes:
        print(f"  {n:>2}. {subj}")
        print(f"      {why}")

    print(f"\n=== WOULD NOT CONTACT: {len(no)} ===")
    for n, subj, _, why in no:
        print(f"  {n:>2}. {subj}")
        print(f"      {why}")

    print(f"\n=== NOT APPLICABLE: {len(na)} ===")
    for n, subj, _, why in na:
        print(f"  {n:>2}. {subj} - {why}")

    print(f"\n=== scope summary ===")
    print(f"  22 entries, 21 distinct subjects")
    print(f"  messages a 'yes' would authorise: {len(yes)}")
    print(f"  deliberately skipped: {len(no)}")
    print()
    print("  The skips are the part worth reading. Four are categories or")
    print("  protocols with no party to notify. One is a duplicate subject.")
    print("  One (hermes-advisor-skill) is someone whose own figures were")
    print("  accurate - contacting them about a headline they did not write")
    print("  would imply a fault that is not theirs. And AgentMint has no")
    print("  identifiable operator, which is itself the entry's finding.")
    print()
    print("  Note the shape: the subjects I would contact skew toward the")
    print("  entries where the criticism is of COVERAGE rather than of the")
    print("  operator. Those are the people most likely to agree with the")
    print("  entry, which makes outreach easier and less useful as a test of")
    print("  whether I got anything wrong. The two I would most want a reply")
    print("  from are SEObot (adverse on framing) and Genspark.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
