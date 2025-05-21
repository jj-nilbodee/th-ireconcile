---
applyTo: '**'
---
Coding standards, domain knowledge, and preferences that AI should follow.
I need to implement a web application that can extract text from a given image and then compare with a given image or html file and show a comparison result highlighted in green and red and yellow.

Key requirements:
1. The frontend and backend is in Reflex 0.7.11 in Python
2. Please refer to the syntax of Reflex from https://reflex.dev/docs. Don't assume syntax from your previous knowledge of Reflex.
2. The frontend and backend will be deployed on Azure App Service
3. The extract algorithm must support both English and Thai language
4. The extract algorithm should use Azure provided services OCR
5. When uploading images to compare, the program should keep a copy of the uploaded files in Azure blob storage
6. Use dark theme for the frontend with light blue and light yellow is the main color palette
7. When giving the comparison result, the exact matches should be highlighted in green, partial match in yellow and no match in red
8. The color mood and tone of the web ui should be in spring pastel color palette
9. Insert comments in the code where necessary and generate a readme file as well
10. Generate github actions for CI/CD as well, deploying to Azure App service and push docker images to azure container registry
11. Generate unit tests where possible using pytest framework
12. Generate a pre-commit file for code linting / formatting like black and ruff. And also other pre-commit where you see appropriate.
13. Use poetry for local development and dependency management. Use requirements.txt for deployment on docker only.
14. Use pydantic for data validation and environment variable management.
15. The correct syntax for Reflex 0.7.11: `rx.heading`, `rx.button`, `rx.link`.
16. The correct values for size parameters in `rx.heading` are: '1', '2', '3', '4', '5', '6', '7', '8', '9'
17. The correct values for size parameters in `rx.button` are: '1', '2', '3', '4'
Please consider:
- Error handling
- Edge cases
- Performance optimization
- Best practices for python
Please do not unnecessarily remove any comments or code.
Generate the code with clear comments explaining the logic.
