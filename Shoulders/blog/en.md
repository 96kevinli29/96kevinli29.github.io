title: What AI’s mathematics is built on
desc: We parsed the references of OpenAI’s 722 AI-written math manuscripts: 11,067 human works by 9,612 mathematicians. What that says about how models learn, and why scientists still steer.
kicker: Essay · Sea-Fill · 9 October 2026

# What AI’s mathematics is built on

After OpenAI released 722 AI-written mathematics manuscripts, we did the slow, careful work: we wrote code to extract every reference list, then checked them one by one.

The result: 11,067 human works by 9,612 mathematicians.[^1]

One of the manuscripts, on four-dimensional Kakeya sets, has 34 references. The oldest is Besicovitch’s paper of 1928. After it come Davies, Wolff, Katz, Łaba, Tao and Guth, all the way to Hong Wang and Joshua Zahl’s work in 2026.

We work in AI ourselves. We did this because results like these are often reported as “AI solves X”, as if no one stood behind them. We wanted to know who does.

## How a model capable of scientific breakthroughs is built

Many people contribute to a model capable of scientific breakthroughs. Two groups are most closely tied to it. Engineers build the machine: the architecture, the training code, the data pipelines, the compute. Scientists supply much of what the machine learns from and what it aims at. Training has three stages, and both groups are present in each.

**Pretraining.** Engineers build a system that learns to predict the next token from the text before it. Almost everything it learns at this stage comes from a vast amount of unstructured text that people wrote. One of the AI manuscripts contains the step “by the splitting theorem for vector bundles on the projective line, E is a direct sum of line bundles”. A model that writes this step has learned that the second half is very likely to follow the first. It did not discover the fact. Grothendieck proved it in 1957, and mathematicians have written that step in papers, textbooks and lecture notes ever since. That is where the probability comes from. Mathematicians call it intuition when they know which lemma to reach for next; a model’s version of it is a set of conditional probabilities estimated from the next steps that people wrote down. Minimising prediction error is, in information-theoretic terms, compression, and what the parameters can hold depends on what went in.

**Supervised fine-tuning.** Post-training for reasoning models often begins with what is called a cold start: fine-tuning on a smaller, carefully chosen set of long chains of reasoning that show, step by step, how problems are solved. DeepSeek’s public report on its R1 model, for example, describes such a stage.[^3] Engineers assemble and run it. The chains themselves are a mix. Some are written by people: proofs, derivations, worked solutions, annotated reasoning. Many are synthesised by models. But the synthetic ones still start from problems and instructions that people wrote, imitate the way human proofs are written, and are kept or thrown away by checks that people designed. What the model learns here is how a mathematician gets from one step to the next.

**Reinforcement learning.** Engineers build the loop: the model tries a problem many times, a verifier checks the attempts, and training makes the successful paths more likely. What the loop needs from outside is problems worth practising on, a precise definition of a correct answer, and someone to judge what comes out. Today those still come largely from scientists, as we explain below.

This is why the quality of scientific data matters so much. Reinforcement learning can only strengthen what the model already produces when it samples. If a model almost never writes a correct proof, almost every reward is zero and there is almost nothing to learn from; the search is too inefficient to get anywhere. What raises the chance of a correct attempt from almost never to sometimes is the quality of what came before: careful proofs in the pretraining text, clean chains of reasoning in fine-tuning. A model trained on sloppy or shallow mathematics samples sloppy, shallow attempts. High-quality scientific writing is a large part of what makes efficient sampling possible. How far reinforcement learning can go beyond what the base model already contains is still an open research question; that it starts from there is not.

Put simply: the engineers’ work makes the learning possible, and much of what there is to learn comes from scientists.

## What the references show

We cannot see what a model learned from which text. A reference list is the one part we can see and check.

The 11,067 works include 114 Fields, Abel and Wolf laureates. The citations are not decoration. In the citing sentences, the manuscripts use these works as tools:

- To split a vector bundle, a manuscript uses Grothendieck’s theorem of 1957.
- To confirm that a construction is algebraic, one invokes Serre’s GAGA of 1956. That paper is cited by 13 manuscripts.
- In a Ricci-flow argument, one uses Perelman’s 2002 entropy monotonicity to carry a weighted Sobolev inequality forward in time.
- To build obstructions on four-manifolds, several use the Chern–Simons transgression functional of Shiing-Shen Chern and James Simons, from 1974.
- A counterexample in combinatorics follows the incidence and sum–product strategy of Bourgain, Katz and Tao.
- To bound a variance in a percolation model, one applies the Brascamp–Lieb inequality of 1976.
- To handle Hodge structures, one uses Deligne’s semisimplicity argument.

## Whose problems these are

Then there are the problems themselves.

The first results in OpenAI’s catalogue are on Milne’s rationality conjecture, the Birch–Swinnerton-Dyer formula and a “quasi-Riemann hypothesis”. Further down are Kaplansky’s direct-finiteness conjecture, the Mahler conjectures, the Mézard–Parisi formula, Hilbert’s tenth problem over the rationals, the Kakeya conjecture and the Navier–Stokes equations. Almost every one carries the name of the person who asked it.

Erdős’s 1957 list “Some unsolved problems” is cited by 5 manuscripts. Shing-Tung Yau’s 1994 “Open problems in geometry” is cited by 4. OpenAI’s repository says that they “evaluate our models on open research problems”. The supply of good open problems is something mathematicians have built up over centuries.

## A long relay

The four-dimensional Kakeya manuscript builds on Hong Wang and Joshua Zahl’s recent breakthrough on the Kakeya conjecture in three dimensions. That work in turn stands on the line from Besicovitch through Wolff, Katz, Łaba, Tao and Guth.

On the Bochner–Riesz problem, which is closely tied to Kakeya, AI manuscripts repeatedly cite the 2025 paper of Shaoming Guo with Changkeun Oh, Hong Wang, Shukun Wu and Ruixiang Zhang. They place it beside Tao’s 2003 bilinear restriction estimate as a source of the wave-packet method they use, and one of them adopts its pseudoconformal change of variables.

Chinese mathematicians are part of this relay:

- A manuscript on the abundance conjecture follows the foliation criterion of Chenyang Xu and Lei Zhang.
- A manuscript on hard-sphere gases imports estimates from Yu Deng, Zaher Hani and Xiao Ma’s derivation of the Boltzmann equation from particle dynamics. Deng received a Fields Medal this year.
- Shing-Tung Yau’s 1978 proof of the Calabi conjecture is cited by 10 manuscripts.
- Gang Tian’s book with John Morgan on the Ricci flow and the Poincaré conjecture, Jian Ding’s proof of the satisfiability conjecture with Allan Sly and Nike Sun, and C. N. Yang’s 1957 paper with T. D. Lee and Kerson Huang on the hard-sphere Bose gas are all in the references.

The same holds outside this release. OpenAI’s Navier–Stokes paper starts from the equations Euler wrote in 1757, then recalls Leray’s weak solutions of 1934 and the partial regularity theorem of Caffarelli, Kohn and Nirenberg. AlphaFold was trained on protein structures that structural biologists solved one at a time over decades; its premise goes back to Anfinsen’s 1973 finding that a protein’s sequence determines its shape.

## What the references don’t show

A reference list is the visible part. It does not show the textbooks nobody cites, the teachers who passed these ideas on, the referees who checked the papers, or the attempts that failed and were never published but taught others which roads lead nowhere. All of that went into the text that models learn from. None of it has a name in our data.

## Where scientists come in next

Pretraining and supervised fine-tuning give a model its intuitions and its way of reasoning. New results at the frontier usually come from reinforcement learning: the model makes many attempts at a problem, called rollouts, a verifier checks them, and training makes the successful paths more likely. Successful trajectories can then become training data for the next round.

From a training point of view, human scientists sit at three points in this loop.

**They choose the problems.** Reinforcement learning learns most from problems that are just within reach. If every rollout succeeds, there is no signal; if every rollout fails, the reward is zero and so is the gradient. The useful problems are the ones at the edge of what the model can do that also lead somewhere that matters. Good problems produce good seeds for the next round; poor problems produce poor ones. Picking them takes the judgement that mathematicians call taste. Lists like those of Erdős, Yau and Hilbert are exactly this kind of work.

**They define what counts as correct.** If a reward is specified loosely, a model learns to exploit the gap. Mathematics works as a testing ground because mathematicians have defined proof precisely. OpenAI’s Navier–Stokes paper states that it establishes alternative (C) “in the Millennium problem statement for Navier–Stokes as stated by Fefferman”, and it checks a condition on the pressure that comes from the erratum to that statement. Its Lean formalization rests on Mathlib, an open library of formalized mathematics built over many years by mathematicians and programmers. The verifier is human work too.

**They judge the results.** On 7 October, OpenAI withdrew 3 manuscripts after a sign error was found, and revised 14 others. Their repository notes that some of the unformalized results “could have issues”. Deciding which results hold, which matter and which directions deserve the next round of compute is still the work of the scientific community.

That is why we do not see scientists being replaced. In the loop above, they choose the problems, define correctness and judge the results. We would call that navigating.

## Why it matters now

Models do not create new human knowledge on their own. Research has found that models trained repeatedly on model-generated data lose the rare parts of their distribution and degrade.[^2] New problems, new ideas and new experimental data still have to come from people.

If the common story becomes “AI solves it, scientists are no longer needed”, that story will affect where research funding goes. It will also affect whether young people choose to spend years on a hard problem with no guaranteed result. Fewer of them would mean less of the material that models learn from, and fewer people to steer.

## What we built

For most of history, this was solitary work: the people who did it had no machine to ask. Many of them are in our list. Many more are not.

So we built On Whose Shoulders, an open-source record of the human work that AI results in science build on, organised by field and updated as new results appear. You can type any scientist’s name and see which of their works the AI manuscripts use. It also covers OpenAI’s Navier–Stokes papers and AlphaFold.

If you write about AI results in science, please name the people behind them. Our data is open for that.

Scientists are the bridge between human knowledge and AI, and we want their names to stay attached to what is built on them.

[Explore On Whose Shoulders →](../)

[^1]: OpenAI released 722 manuscripts on 6 October 2026. On 7 October it withdrew 3 and revised 14; our counts use the 719 current manuscripts. Data: github.com/openai/math (Apache 2.0).
[^2]: I. Shumailov et al., “AI models collapse when trained on recursively generated data”, Nature 631, 755–759 (2024).
[^3]: DeepSeek-AI, “DeepSeek-R1: Incentivizing Reasoning Capability in LLMs via Reinforcement Learning” (2025).
