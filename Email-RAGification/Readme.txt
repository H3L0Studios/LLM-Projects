This project will load a collection of emails (of any size) into a vector database. if relevant, Emails from the database can be passed to the openAI model queries to add context it would not otherwise have.

To use this, you need to provide an .mbox export from your email app. GMAIL does this for example.

Had some good results, for example asking: "Please list all phone numbers from emails and who they belong to." -or- "please summarize all emails regarding personal matters with <my wife's name>".

One note, I included chunking code but got better results without it. It is only necessary if you have a lot of really long email threads.
If you do use it, change this:
vectorstore = Chroma.from_documents(documents=documents, embedding=embeddings, persist_directory=db_name)

to this:

vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings, persist_directory=db_name)