from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate
from parsers import type_parser

type_system_prompt = '''Ты — классификатор намерений пользователя. Твоя задача — прочитать сообщение пользователя и определить, какое из четырёх действий он хочет выполнить. Ответь строго одной из следующих фраз без каких-либо дополнительных слов, пояснений или форматирования:

1. Добавить задачу (add) — если пользователь хочет создать новую задачу (например: «Добавь задачу „Купить хлеб“», «Напомни мне позвонить маме»).
2. Изменить задачу (manage) — если пользователь хочет отредактировать или обновить существующую задачу (например: «Измени дедлайн у задачи про отчёт», «Поменяй описание задачи „Подготовить презентацию“»).
3. Получить задачу (get) — если пользователь запрашивает информацию о задачах: список, детали, статус и т.п. (например: «Какие у меня задачи?», «Покажи задачу про встречу», «Посоветуй чем заняться»).
4. Просто поговорить (talk) — если сообщение не связано с управлением задачами: приветствия, общие вопросы, фразы вроде «Привет», «Как дела?», «Расскажи анекдот» и т.д.

ВАЖНО: твой ответ должен содержать только одну из этих четырёх фраз дословно: «add», «manage», «get» или «talk».
'''

type_human_prompt_template = """Проанализируй следующий запрос:
{user_input}

{format_instructions}

ТОЛЬКО JSON!"""

type_human_prompt = HumanMessagePromptTemplate.from_template(
    template=type_human_prompt_template,
    input_variables=['user_input'],
    partial_variables={'format_instructions': type_parser.get_format_instructions()}
)

type_prompt = ChatPromptTemplate.from_messages([
    ('system', type_system_prompt),
    type_human_prompt
])

