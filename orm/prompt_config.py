from typing import Any

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Time, Boolean, DECIMAL, Enum, Text

engine = create_engine('sqlite:////sqlite3/llm.db', echo=False)
# 建立基本映射类
Base = declarative_base()
# 创建会话
Session = sessionmaker(bind=engine)


class PromptConfig(Base):
    __tablename__ = 'prompt_config'
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=True, unique=True)
    document_type = Column(String, nullable=True)
    lang = Column(String(50), nullable=True, default="English")
    model = Column(String, nullable=True, default="none")
    # 0-语种和票据类型识别 1-ocr 2-翻译
    prompt_type = Column(String, nullable=True)
    prompt = Column(Text, nullable=True, default="none")

    def __init__(self, **kw: Any):
        super().__init__(**kw)
        self.session = Session()
        # 创建数据表
        Base.metadata.create_all(engine, checkfirst=True)

    def __repr__(self):
        return "<PromptConfig(id='%s',lang='%s',prompt_type='%s',model='%s',document_type='%s')>" % (
            self.id, self.lang, self.prompt_type, self.model, self.document_type)

    def add(self, prompt):
        self.session.add(prompt)
        # 提交事务
        self.session.commit()

    def remove(self, prompt):
        _id = prompt['id']
        prompt = self.session.query(PromptConfig).filter_by(id=_id)
        self.session.delete(prompt)
        self.session.commit()

    def query_all(self, params: dict):
        prompt = self.session.query(PromptConfig).filter_by(**params).all()
        return prompt

    def load_all_cache(self):
        rows = self.session.query(PromptConfig).all()
        cache = {}
        for row in rows:
            prompt_type = row.prompt_type
            model = row.model
            document_type = row.document_type
            lang = row.lang
            prompt = row.prompt

            if prompt_type not in cache:
                cache[prompt_type] = {model: {document_type: {lang: prompt}}}
            else:
                prompt_type_cache = cache[prompt_type]
                if model not in prompt_type_cache:
                    cache[prompt_type][model] = {document_type: {lang: prompt}}
                else:
                    model_cache = prompt_type_cache[model]
                    if document_type not in model_cache:
                        cache[prompt_type][model][document_type] = {lang: prompt}
                    else:
                        document_type_cache = model_cache[document_type]
                        if lang not in document_type_cache:
                            cache[prompt_type][model][document_type][lang] = prompt

        return cache

    def update(self, _id, data: dict):
        prompt = self.session.query(PromptConfig).filter_by(id=_id).first()
        if 'lang' in data:
            prompt.lang = data['lang']
        if 'document_type' in data:
            prompt.document_type = data['document_type']
        if 'model' in data:
            prompt.model = data['model']
        if 'prompt_type' in data:
            prompt.prompt_type = data['prompt_type']
        if 'prompt' in data:
            prompt.model = data['prompt']

        self.session.commit()


if __name__ == '__main__':
    prompt_config = PromptConfig()

    prompt_list = prompt_config.load_all_cache()
    print(prompt_list)

    print(prompt_list['2']['internvl2-26b']['invoice']['English'])

    print(list(list(list(prompt_list['0'].values())[0].values())[0].values())[0])
