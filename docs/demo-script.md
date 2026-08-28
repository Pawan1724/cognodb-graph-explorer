# Wexa AI Take-Home: Demo Script (CognoDB Graph Explorer)

*Goal: Keep it under 3 minutes, focusing heavily on the "Why a graph database" aspect of the assignment.*

## 0:00 – 0:20 | Introduction
*(Screen showing the main dashboard with a blank or welcome state)*
"Hi, I'm Pawan. This is **CognoDB Graph Explorer**, my submission for the Wexa AI take-home assignment. It's a full-stack application built with FastAPI and React, completely powered by a CognoDB graph database."

## 0:20 – 0:50 | The Problem & Architecture
*(Briefly show the architecture diagram or data model in the README, then back to the app)*
"In most companies, workplace data is siloed. HR knows who works where, Jira tracks tasks, Outlook tracks emails. 
I built this tool to unify those silos into a single knowledge graph. People, Companies, Projects, Tasks, and Meetings are all represented as Nodes, connected by typed relationships like `WORKS_ON` or `ATTENDED`."

## 0:50 – 1:30 | The "Relationally Awkward" Query
*(Typing the following query into the search bar)*
**Query to type:** *"Show me everyone connected to the Apollo project through either meetings or tasks."*
"If we tried to answer this question with SQL, we'd be joining five or six tables just to find all the possible paths. It gets incredibly slow and complicated."

*(Hit enter, wait for results)*
"But because we're using CognoDB, relationships are first-class citizens. The DeepSeek AI safely translates my English question into a parameterized Cypher query in the background."

## 1:30 – 2:00 | Cypher Translation
*(Point to the generated Cypher in the UI if visible, or explain it)*
"Here, the AI generated a Cypher `UNION`. The first part traverses `(Person)-[:ATTENDED]->(Meeting)-[:RELATED_TO]->(Project)`. The second part traverses `(Person)-[:ASSIGNED_TO]->(Task)-[:BELONGS_TO]->(Project)`. It's a true multi-hop traversal."

## 2:00 – 2:40 | Visualizing the Graph
*(Scroll to the interactive graph visualization)*
"And here are the results returned directly from CognoDB. Because the AI is instructed to return the full Node entities and their relationships, the frontend can render this beautiful layered visualization. 
You can instantly see exactly how each person is connected to the Apollo project—whether they attended a meeting, or if they're assigned to a specific task for the project."

## 2:40 – 3:00 | Conclusion
*(Show the result table or wrap up)*
"This demonstrates exactly why a graph database is the right tool for workplace analytics. It makes complex, multi-hop relationship discovery trivial. The code is secure, uses strict parameterization, and gracefully handles database outages. 
Thank you for watching!"
