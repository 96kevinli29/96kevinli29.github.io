title: What AI’s mathematics is built on
desc: We parsed the references of OpenAI’s 722 AI-written math manuscripts: 11,067 human works by 9,612 mathematicians. What that says about how models learn, and why scientists still steer.
kicker: DATA ESSAY · 9 OCTOBER 2026
dek: We wrote code to extract every reference in OpenAI’s 719 AI-written mathematics manuscripts, then checked them one by one. Behind them stand **11,067 human works by 9,612 mathematicians**.
byline: By **Hongyang Li** and the Sea-Fill team

# What AI’s mathematics | is built on

After OpenAI released 722 AI-written mathematics manuscripts [@openai_math], we did the slow, careful work: we wrote code to extract every reference list, then checked them one by one.

One of the manuscripts, on four-dimensional Kakeya sets, has 34 references. The oldest is Besicovitch’s paper of 1928. After it come Davies, Wolff, Katz, Łaba, Tao and Guth, all the way to Hong Wang and Joshua Zahl’s work in 2026 [@besicovitch1928; @davies1971; @wolff1995; @klt2000; @guth2010; @wangzahl2026].

We work in AI ourselves. We did this because results like these are often reported as “AI solves X”, as if no one stood behind them. We wanted to know who does.

## Engineers build the machine; scientists give it something to learn

Many people contribute to a model capable of scientific breakthroughs. Two groups are most closely tied to it. Engineers build the machine: the architecture, the training code, the data pipelines, the compute. Scientists supply much of what the machine learns from and what it aims at. Training has three stages, and both groups are present in each.

**Pretraining.** Engineers build a system that learns to predict the next token from the text before it [@brown2020]. Almost everything it learns at this stage comes from a vast amount of unstructured text that people wrote. One of the AI manuscripts contains the step “by the splitting theorem for vector bundles on the projective line, E is a direct sum of line bundles”. A model that writes this step has learned that the second half is very likely to follow the first. It did not discover the fact. Grothendieck proved it in 1957 [@grothendieck1957], and mathematicians have written that step in papers, textbooks and lecture notes ever since. That is where the probability comes from. Mathematicians call it intuition when they know which lemma to reach for next; a model’s version of it is a set of conditional probabilities estimated from the next steps that people wrote down. Minimising prediction error is, in information-theoretic terms, compression [@shannon1948; @deletang2024], and what the parameters can hold depends on what went in.

{{fig:stage_pre}}

**Supervised fine-tuning.** Post-training usually pairs supervised fine-tuning with reinforcement learning [@ouyang2022]. For reasoning models it often begins with what is called a cold start: fine-tuning on a smaller, carefully chosen set of long chains of reasoning that show, step by step, how problems are solved. DeepSeek’s public report on its R1 model, for example, describes such a stage [@deepseek2025]. Engineers assemble and run it. The chains themselves are a mix. Some are written by people: proofs, derivations, worked solutions, annotated reasoning. Many are synthesised by models. But the synthetic ones still start from problems and instructions that people wrote, imitate the way human proofs are written, and are kept or thrown away by checks that people designed. What the model learns here is how a mathematician gets from one step to the next.

{{fig:stage_sft}}

**Reinforcement learning and search at test time.** Engineers build the loops. In training, the model tries a problem many times, a verifier checks the attempts, and training makes the successful paths more likely [@shao2024; @deepseek2025]. At test time, the same idea is spent as compute: sample many attempts, search among them, keep the ones a verifier accepts [@wang2022sc; @lightman2023; @snell2024]. Increasingly this is organised as agents that write code, call proof assistants and check one another’s work [@yao2022]. What these loops need from outside is problems worth practising on, a precise definition of a correct answer, and someone to judge what comes out. Today those still come largely from scientists, as we explain below.

{{fig:stage_rl}}

{{fig:stages}}

This is why the quality of scientific data matters so much. Reinforcement learning, test-time search and agents all work by sampling: they can strengthen or find only what the model can already produce. If a model almost never writes a correct proof, almost every reward is zero and there is almost nothing to learn from, and no amount of sampling at test time will turn one up; the search is too inefficient to get anywhere. What raises the chance of a correct attempt from almost never to sometimes is the quality of what came before: careful proofs in the pretraining text, clean chains of reasoning in fine-tuning [@lewkowycz2022; @gunasekar2023]. A model trained on sloppy or shallow mathematics samples sloppy, shallow attempts. High-quality scientific writing is a large part of what makes efficient sampling possible. How far reinforcement learning can go beyond what the base model already contains is still an open research question [@yue2025]; that it starts from there is not.

{{fig:sampling}}

Put simply: the engineers’ work makes the learning possible, and much of what there is to learn comes from scientists.

## 11,067 works, used as tools

We cannot see what a model learned from which text. A reference list is the one part we can see and check.

They also reach a long way back. The oldest cited work is Descartes’s *La Géométrie* of 1637 [@descartes1637]; the manuscript on a “quasi-Riemann hypothesis” cites Riemann’s own paper of 1859 [@riemann1859].

{{fig:decades}}

The 11,067 works include 114 Fields, Abel and Wolf laureates. Most of the authors are not names from history books but mathematicians working today. And the citations are not decoration. In the citing sentences, the manuscripts use their work as tools:

- A manuscript on local smoothing names exactly two external inputs to its proof: Kevin Ren and Hong Wang’s planar Furstenberg theorem, and the wave-envelope theorem of Larry Guth, Hong Wang and Ruixiang Zhang [@renwang2025; @guthwangzhang2020].
- In arithmetic geometry, a manuscript identifies certain vector bundles with p-adic local systems “by [Fargues–Scholze 2024]”, the work of Laurent Fargues and Peter Scholze [@farguesscholze2024].
- In birational geometry, one follows a recent strategy of Caucher Birkar and a coauthor, and another applies Birkar’s theorem on bounded complements [@birkar2019]; others build on Osamu Fujino’s inductions and on the work of Omprokash Das, Christopher Hacon and Mihai Păun [@dashaconpaun2024].
- In probability, manuscripts rely on the properties of the random-cluster model as set out by Hugo Duminil-Copin and his coauthors [@dchn2011], and on the random-surface laws of Bertrand Duplantier, Jason Miller and Scott Sheffield [@dms2021].
- A counterexample in graph theory uses László Lovász and Balázs Szegedy’s sampling construction for graphons [@lovaszszegedy2006]; one in combinatorics follows the sum–product strategy of Jean Bourgain, Nets Katz and Terence Tao [@bkt2004].
- A manuscript on spin glasses uses Michel Talagrand’s cavity method [@talagrand2011].
- In a Ricci-flow argument, one uses Grigori Perelman’s 2002 entropy monotonicity [@perelman2002]; in Hodge theory, one uses Pierre Deligne’s semisimplicity argument [@deligne1982].

Each field rests on its own people.

{{fig:tree_fields}}

## The problems carry human names

Then there are the problems themselves.

The first results in OpenAI’s catalogue are on Milne’s rationality conjecture, the Birch–Swinnerton-Dyer formula and a “quasi-Riemann hypothesis”. Further down are Kaplansky’s direct-finiteness conjecture, the Mahler conjectures, the Mézard–Parisi formula, Hilbert’s tenth problem over the rationals, the Kakeya conjecture and the Navier–Stokes equations. Almost every one carries the name of the person who asked it.

Erdős’s 1957 list “Some unsolved problems” is cited by 5 manuscripts [@erdos1957]. Shing-Tung Yau’s 1994 “Open problems in geometry” is cited by 4 [@yau1994]. OpenAI’s repository says that they “evaluate our models on open research problems”. The supply of good open problems is something mathematicians have built up over centuries.

## A century-long relay

The four-dimensional Kakeya manuscript builds on Hong Wang and Joshua Zahl’s recent breakthrough on the Kakeya conjecture in three dimensions [@wangzahl2025; @wangzahl2026]. That work in turn stands on the line from Besicovitch through Wolff, Katz, Łaba, Tao and Guth [@wolff1995; @klt2000; @bct2006; @guth2010].

{{fig:tree_kakeya}}

On the Bochner–Riesz problem, which is closely tied to Kakeya, AI manuscripts repeatedly cite the 2025 paper of Shaoming Guo with Changkeun Oh, Hong Wang, Shukun Wu and Ruixiang Zhang [@gowwz2025]. They place it beside Tao’s 2003 bilinear restriction estimate [@tao2003] as a source of the wave-packet method they use, and one of them adopts its pseudoconformal change of variables.

Chinese mathematicians are part of this relay:

- A manuscript on the abundance conjecture follows the foliation criterion of Chenyang Xu and Lei Zhang [@xuzhang2019].
- A manuscript on hard-sphere gases imports estimates from Yu Deng, Zaher Hani and Xiao Ma’s derivation of the Boltzmann equation from particle dynamics [@denghanima2025]. Deng received a Fields Medal this year.
- Shing-Tung Yau’s 1978 proof of the Calabi conjecture is cited by 10 manuscripts [@yau1978].
- Gang Tian’s book with John Morgan on the Ricci flow and the Poincaré conjecture [@morgantian2007], Jian Ding’s proof of the satisfiability conjecture with Allan Sly and Nike Sun [@dingslysun2022], and C. N. Yang’s 1957 paper with T. D. Lee and Kerson Huang on the hard-sphere Bose gas [@leehuangyang1957] are all in the references.

The same holds outside this release. OpenAI’s Navier–Stokes paper [@openai_ns] starts from the equations Euler wrote in 1757 [@euler1757], then recalls Leray’s weak solutions of 1934 [@leray1934] and the partial regularity theorem of Caffarelli, Kohn and Nirenberg [@ckn1982]. AlphaFold [@jumper2021] was trained on protein structures that structural biologists solved one at a time over decades; its premise goes back to Anfinsen’s 1973 finding that a protein’s sequence determines its shape [@anfinsen1973].

{{fig:tree_ns}}

{{fig:tree_af}}

## Scientists supply the signal

Pretraining and supervised fine-tuning give a model its intuitions and its way of reasoning. New results at the frontier come from sampling on a large scale: reinforcement learning during training, and search and agents at test time. In each, the model makes many attempts at a problem, called rollouts, and a verifier decides which ones count. Successful trajectories can then become training data for the next round [@zelikman2022].

In the language of training, a gradient is what a model learns from one example, and it is only as good as the signal behind it. Much of the strong signal comes from scientists: carefully written proofs give pretraining clear next steps to learn; well-chosen problems keep rewards from being all zeros or all ones; precise verifiers make sure the signal points the right way. Whether the sampling happens in training or at test time, scientists sit at three points in the loop.

**They choose the problems.** Training learns most, and test-time compute is best spent, on problems that are just within reach. If every rollout succeeds, there is no signal; if every rollout fails, the reward is zero and so is the gradient [@shao2024]. The useful problems are the ones at the edge of what the model can do that also lead somewhere that matters. Good problems produce good seeds for the next round; poor problems produce poor ones. Picking them takes the judgement that mathematicians call taste. Lists like those of Erdős, Yau and Hilbert are exactly this kind of work.

**They define what counts as correct.** In training the verifier sets the reward; at test time it decides which of many attempts is kept. If it is specified loosely, a model learns to exploit the gap [@amodei2016; @skalse2022]. Mathematics works as a testing ground because mathematicians have defined proof precisely. OpenAI’s Navier–Stokes paper states that it establishes alternative (C) “in the Millennium problem statement for Navier–Stokes as stated by Fefferman” [@fefferman2000], and it checks a condition on the pressure that comes from the erratum to that statement. Its Lean formalization rests on Mathlib [@mathlib2020], an open library of formalized mathematics built over many years by mathematicians and programmers. The verifier is human work too.

**They judge the results.** On 7 October, OpenAI withdrew 3 manuscripts after a sign error was found, and revised 14 others. Their repository notes that some of the unformalized results “could have issues”. Deciding which results hold, which matter and which directions deserve the next round of compute is still the work of the scientific community.

So however capable AI becomes, it needs navigators. Drilling for oil is a fair comparison: however powerful the rig, a geologist still decides where to drill and whether what comes up is oil. In the loop above, scientists choose the problems, define correctness and judge the results; AI makes attempts on a scale no person could.

This is a collaboration. Each turn of the loop produces new data that carries a learning signal: proofs that pass, ideas that are ruled out, the next question worth asking. That data in turn makes the next model better. We do not see scientists being replaced. Their work has gained a role: navigating.

{{fig:loop}}

## If scientists step back, the gradient signal fades

Models can produce new results; this release shows it. But how far they reach depends on their instruments: the problems they are pointed at, the verifiers that recognise a correct answer, the data that shapes what they sample. Without good instruments, sampling does not land on new knowledge. And a model fed mainly on its own output loses ground: research has found that models trained repeatedly on model-generated data lose the rare parts of their distribution and degrade [@shumailov2024]. New problems, new ideas, new experimental data, and the instruments to check them, still come largely from people.

If the common story becomes “AI solves it, scientists are no longer needed”, that story will affect where research funding goes. It will also affect whether young people choose to spend years on a hard problem with no guaranteed result. Fewer of them would mean less of the material that models learn from, and fewer people to steer.

## The names that are missing

A reference list is the visible part. It does not show the textbooks nobody cites, the teachers who passed these ideas on, the referees who checked the papers, or the attempts that failed and were never published but taught others which roads lead nowhere. All of that went into the text that models learn from. None of it has a name in our data.

For most of history, this was solitary work: the people who did it had no machine to ask. Many of them are in our list. Many more are not.

Scientists are the bridge between human knowledge and AI, and we want their names to stay attached to what is built on them.

{{cta}}

## Writing the names down

On Whose Shoulders is an open-source record of the human work that AI results in science build on. Type any scientist’s name and see which of their works the AI manuscripts use. If you write about AI results in science, please name the people behind them.

[Explore On Whose Shoulders →](../)

[Download all references (BibTeX)](references.bib)

[^1]: OpenAI released 722 manuscripts on 6 October 2026. On 7 October it withdrew 3 and revised 14; our counts use the 719 current manuscripts. Data: github.com/openai/math (Apache 2.0).
