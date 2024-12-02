"""
This class uses SQLAlchemy to handle conversion to and from Pandas DataFrame & SQL
"""

from typing import Type, Union, List
import pandas as pd
import pandas.api.types as ptypes
import re
from sqlalchemy import MetaData, Table, Column, Integer, String, DateTime, Float

def _infer_sql_type(dtype) -> Type[Union[Integer, DateTime, String, Float]]:
    type_mapping = {
        'integer': Integer,
        'datetime64': DateTime,
        'string': String,
        'bool': Integer,
        'float': Float,
        'object': String
    }
    for pdt, sqt in type_mapping.items():
        check = getattr(ptypes, f'is_{pdt}_dtype')
        if check(dtype):
            return sqt
    return String

def to_snake_case(name: str) -> str:
    name = re.sub(r'\s+', '_', name)
    return re.sub(r'[^\w_]', '', name).lower()

"""
Converts the columns to SQL format for use in CREATE TABLE statements
"""
def columns_from_df(table_name: str, df: pd.DataFrame) -> list[str]:
    metadata = MetaData()
    columns = [
        Column(to_snake_case(col), _infer_sql_type(df[col].dtype))
        for col in df.columns
    ]
    table = Table(to_snake_case(table_name), metadata, *columns)
    columns_with_types = [f"{col.name} {str(col.type)}" for col in table.columns]

    return columns_with_types

"""
Converts the rows to SQL format for use in INSERT statements
"""
def rows_from_df(df: pd.DataFrame) -> List:
    if df.empty:
        return []
    else:
        df_cleaned = df.fillna('NULL')
        return df_cleaned.values.tolist()
