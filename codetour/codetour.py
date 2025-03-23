import subprocess
from git import Repo, Git
from unidiff import PatchSet
from dotenv import load_dotenv
import os
from mistralai import Mistral
import html
import time

class CodeTour:
    @staticmethod
    def tour(commit: str, repository: str) -> None:
        """
        Perform a code tour starting from a specific commit in a repository.
        Args:
            commit (str): A git SHA representing the commit to start the tour from.
            repository (str): A path to a local repository or a GitHub URL.
        Returns:
            None
        """
        repo = Repo(repository)

        load_dotenv()
        api_key = os.environ.get("MISTRAL_API_KEY")
        if api_key:
            print(f"MISTRAL_API_KEY loaded successfully.")
        else:
            print(f"Error: MISTRAL_API_KEY not found in environment variables.")
        model = "mistral-small-latest"

        client = Mistral(api_key=api_key)


        # Get the list of changes in the selected commit using GitPython
        commit_obj = repo.commit(commit)
        commit_message = commit_obj.message.strip()
        commit_hash = commit_obj.hexsha
        num_files_changed = len(commit_obj.stats.files)

        # print(commit_obj)
        diffs = commit_obj.diff(other=commit_obj.parents[0], create_patch=True)

        # print(f"Stats: {commit_obj.stats.total}")
        
        # for diff in diffs:
        #     print(f"Diff: {diff}")
        
        #     print(f"--- {diff.a_path}")            
        #     if diff.a_blob is not None:
        #         print(diff.a_blob.data_stream.read().decode('utf-8'))

        #     print("a done")


        #     print(f"+++ {diff.b_path}")
        #     if diff.b_blob is not None:
        #         print(diff.b_blob.data_stream.read().decode('utf-8'))
        #     print("b done")

        # Call the git diff command using subprocess
        result = subprocess.run(
            ["git", "--git-dir", f"{repository}/.git", "diff", "--ignore-all-space", "-U0", f"{commit}^", commit],
            capture_output=True,
            text=True
        )
        # print("git")
        # print(result.stdout)

        html_blocks = []
        toc_entries = []
        entries = 0
        patch = PatchSet(result.stdout)
        hunks = 0
        max_hunks = 3
        files = 0
        max_files = 3
        # print(patch)
        for file in patch:
            # print(f"file: '{file}'")

            if files > max_files:
                continue
            files += 1

            for hunk in file:
                print(f"Message: \"{commit_obj.message.strip()}\"")
                print()
                print(f"Hunk Start")
                print(f"{str(hunk).strip()}")
                print(f"Hunk End")

                if hunks > max_hunks:
                    continue
                hunks += 1

                try:
                    chat_response = client.chat.complete(
                        model = model,
                        messages=[
                        {
                            "role": "system",
                            "content":

                            """
                            Your role is to explain code changes succinctly and clearly. 
                            The code changes are submitted to you in the unified diff format.
                            Do not offer suggestions or advice, just explain the code changes.
                            Focus on explaining the "why" and "how" behind the changes rather than describing the changes themselves.
                            Answer with one or two sentences. Do not exceed 1 short paragraph. Keep it "short and sweet".
                            Start your response with "Updates", "Adds", "Removes", etc. and then explain the changes.
        

                            Explain only the code changes you received. 
                            """
                        },
                        
                        {
                            "role": "user", "content":f"{str(hunk).strip()}" 
                        },
                        ],
                    )
                    hunk_description = chat_response.choices[0].message.content
                    # print(chat_response.choices[0].message.content)
                except Exception as e:
                    hunk_description = "Unable to retrieve description. Please try again later."


                # Create HTML content for the hunk and its description
                hunk_code = str(hunk).strip()
                lines_changed = len(hunk_code.split('\n'))

                html_content = f"""
                <div class="tile" id="change-{entries}">
                    <details {"open" if lines_changed < 50 else ""}>
                    <summary>
                        {hunk_description}
                        <div class="metadata">
                            <p>{file.path}: {lines_changed} lines updated</p>
                        </div>
                    </summary>
                    <pre>{html.escape(hunk_code)}</pre>
                    </details>
                </div>
                """

                html_blocks.append(html_content)
                toc_entries.append(f'<li><a href="#change-{entries}">{file.path}</a> <span class="sidebar-change-meta"> {lines_changed} changes </span></li>')
                entries += 1
                # Sleep for a short duration to avoid hitting rate limits
                time.sleep(1)
            
            

        # After the loop, write the HTML content to a file
        html_header = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Code Tour</title>
            <style>
            body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            display: flex;
            flex-direction: row;
            overflow-x: hidden;
            }}
            .sidebar {{
            width: 250px;
            background-color: #f8f9fa;
            padding: 20px;
            height: 100vh;
            overflow-y: auto;
            flex-shrink: 0;
            }}
            .sidebar h2 {{
            font-size: 0.9em;
            color: #333;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding-left: 10px;
            }}
            .sidebar-change-meta {{
            font-size: 0.7em;
            color: #555;
            }}
            .content {{
            flex-grow: 1;
            padding: 20px;
            overflow-y: auto;
            height: 100vh;
            }}
            .tile {{
            border: 1px solid #ccc;
            margin: 10px 0;
            padding: 10px;
            border-radius: 5px;
            background-color: #fff;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            }}
            .description {{
            font-weight: bold;
            margin-bottom: 5px;
            }}
            .metadata {{
            font-size: 0.9em;
            color: #555;
            margin-bottom: 10px;
            }}
            .code-block {{
            background-color: #f9f9f9;
            border: 1px solid #ddd;
            padding: 10px;
            border-radius: 5px;
            }}
            .code-block button {{
            background-color: #007bff;
            color: white;
            border: none;
            padding: 5px 10px;
            cursor: pointer;
            border-radius: 3px;
            }}
            .code-block button:hover {{
            background-color: #0056b3;
            }}
            .code-block pre {{
            margin-top: 10px;
            white-space: pre-wrap;
            word-wrap: break-word;
            }}
            .toc {{
            list-style: none;
            padding: 0;
            padding-left: 10px;
            }}
            .toc li {{
            margin: 5px 0;
            padding-left: 10px;
            border-radius: 3px;
            display: block;
            }}
            .toc a {{
            text-decoration: none;
            padding: 5px;
            }}
            .toc li:hover {{
            background-color: #e9ecef;
            }}
            </style>
        </head>
        <body>
        <div class="sidebar">
            <h2>Changes</h2>
            <ul class="toc">
        """ + "\n".join(toc_entries) + f"""
            </ul>
        </div>
        <div class="content">
        <h1>Code Tour</h1>
        <p><strong>Commit Message:</strong> {commit_message}</p>
        <p><strong>Commit Hash:</strong> {commit_hash}</p>
        <p><strong>Number of Files Changed:</strong> {num_files_changed}</p>
        """

        html_footer = """
        </div>
        </body>
        </html>
        """

        # Combine header, content, and footer
        full_html_content = html_header + "\n".join(html_blocks) + html_footer

        # Write the HTML content to a file
        with open("demo/code_tour.html", "w") as file:
            file.write(full_html_content)


                # print(f"self.source_start = {hunk.source_start}")
                # print(f"self.source_length = {hunk.source_length}")
                # print(f"self.target_start = {hunk.target_start}")
                # print(f"self.target_length = {hunk.target_length}")
                
                
                # for line in hunk:
                #     print(line)
                #     print(line.value)
                #     print(line.source_line_no)
                #     print(line.target_line_no)
                #     print(line.diff_line_no)