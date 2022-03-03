from flask import Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only, decl_api
from sqlalchemy import asc, delete, desc, func, select, update
from sqlalchemy.sql.selectable import Select
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel
from pydantic.utils import Representation

from ..database import models
from ..dependencies.log import logger



class StatusResponse:
    """
    Edit This to add more status
    """
    success = 0
    error = 100
    data_is_not_exist = 101
    data_is_not_updated = 102

class StatusCreator(StatusResponse):
    def __init__(self):
        self._applyStatusAsAttribute()

    def _applyStatusAsAttribute(self):
        allAttr = [i for i in vars(StatusResponse) if not "_" in [i[0], i[-1]]]
        for a in allAttr:
            def fetcher(attrName):
                def response(message: Any = str(attrName).replace("_", " ")):
                    code = StatusResponse.__dict__[attrName]
                    return {
                        "code": code,
                        "message": str(message)
                        }
                return response
            self.__dict__[a] = fetcher(a)

status = StatusCreator()

def create_response(data={}, meta={}, status={}):
    return {
        "data": data,
        "meta": meta,
        "status": status
    }


def extract_single_object(data: decl_api):
    return {k: v for k,v in data.__dict__.items() if "_" not in [k[0], k[-1]]}

def extract_object(data: list):
    datas = []
    for d in data:
        datas.append(extract_single_object(d))
    return datas

def get_field(classModel):
    try:
        fields = [i for i in vars(classModel) if "_" not in [i[0], i[-1]]]
        columnFields = []
        for f in fields:
            if "comparator" in classModel.__dict__[f].__dict__:
                if (
                    "column"
                    in str(classModel.__dict__[f].__dict__["comparator"]).lower()
                ):
                    columnFields.append(f)
        return columnFields
    except:
        return []


def validate_field(modelField, targetField):
    if type(modelField) in [list, tuple, dict]:
        availableField = modelField
    else:
        availableField = get_field(modelField)
    return [i for i in targetField if i in availableField]


class BaseSchema(BaseModel):
    def __init__(
        __pydantic_self__,
        **data: Any
    ) -> None:
        data = __pydantic_self__.filter_data(**data)
        super().__init__(**data)
    
    @classmethod
    def filter_data(cls, **data):
        annots = []
        for relation_class in cls.mro():
            if relation_class not in [BaseSchema, BaseModel, Representation, object]:
                annots.extend(relation_class.__annotations__)
        newData = {}
        for k, v in data.items():
            if k in annots:
                newData[k] = v
        return newData


class QueryPaginationParams:
    """
    Query Params to Paginate the response of the GET Method
    """
    def __init__(
        self,
        fields: Optional[str] = None,
        page: Optional[int] = None,
        limit: Optional[int] = None,
        sortBy: Optional[str] = None,
        sortType: Optional[str] = None,
        **kwargs
    ):
        self.fields = str(fields) if fields else None
        self.page = int(page) if page else 1
        self.limit = int(limit) if limit else 20
        self.sortBy = str(sortBy) if sortBy else None
        self.sortType = str(sortType) if sortType else None    

class Selector:
    """
    Selector Class, modifiying the sqlalchemy select
    """

    def __init__(self, *columns, **columnsKeyPair):
        """
        add your customer key by adding the key-value pair
            ex: Selector(uid = models.User.id, name = models.Profile.name)

        or

        define it automatically by just giving the column name
            ex: Selector(models.User.id, models.Profile.name)

        (this output column name will be user_id, profile_name)
        """
        self.baseClass = models.Base.__subclasses__()
        self.columns = []
        self.columnsKeyPair = {}
        if columns:
            self.columns.extend(columns)
            self.columnsKeyPair.update(dict(zip(self.get_keys(columns), list(columns))))
        if columnsKeyPair:
            self.columns.extend(columnsKeyPair.values())
            self.columnsKeyPair.update(columnsKeyPair)
        self.keys = list(self.columnsKeyPair.keys())

    @property
    def query(self):
        return select(*self.columns)

    def get_keys(self, columns):
        keys = []
        for c in columns:
            className, key = str(c).split(".")
            className = self.check_belonging(className)
            keys.append(className + "_" + key)
        return keys

    def check_belonging(self, key):
        for c in self.baseClass:
            cKey = str(c).split("'")[1].split(".")[-1]
            if key == cKey:
                return c.__tablename__
        return key

    async def execute(self, session: AsyncSession, query: Select):
        data = []
        query = await session.execute(query)
        for q in query:
            data.append(dict(zip(self.keys, list(q))))
        return data

class QueryManager:
    def __init__(self, classModel):
        self.classModel = classModel

    @property
    def fields(self) -> list:
        return get_field(self.classModel)

    @property
    def rawQuery(self) -> Select:
        return select(self.classModel)

    def validate_fields(self, fields: list) -> list:
        if fields:
            return [i for i in fields if i in self.fields]
        return []


def QueryPaginator(
    getParams: QueryPaginationParams, _obj: Union[decl_api.DeclarativeMeta, Selector]
    ):
    """
    Query Paginator generator for single or multiple table
    """
    if type(_obj) == Selector:
        return QueryPaginatorMultiple(getParams, _obj)
    if _obj in models.Base.__subclasses__():
        return QueryPaginatorSingle(getParams, _obj)
    raise BaseException("Error Paginator")


class QueryPaginatorSingle(QueryManager):
    """
    Query Paginator for common use of paginating functions
    """

    def __init__(self, getParams: QueryPaginationParams, classModel):
        QueryManager.__init__(self, classModel)
        self.getParams = getParams
        if getParams.fields:
            self.filterFields = self.validate_fields(getParams.fields.split(","))
        else:
            self.filterFields = self.fields

    def filter(self, query: Select, fields: Optional[list] = None) -> Select:
        """
        filter the desired fields from the query (it will remains the primary key)
        """
        if not fields:
            fields = self.filterFields
        return query.options(load_only(*fields))

    def filter_primary_key(self, data: list) -> list:
        """
        primary key filter
        """
        newData = []
        for d in data:
            newPair = {}
            for key in d.__dict__:
                if key in self.filterFields:
                    newPair[key] = d.__dict__[key]
            newData.append(newPair)
        return newData

    def sort(self, query: Select, sortBy: str, sortType: str) -> Select:
        """
        sort your query by defining both the sortBy 'fields' and sortType 'asc'/'desc' parameters
        """
        if sortBy in self.fields:
            merchantOrder = self.classModel.__dict__[sortBy]
            for iSortType, orderMethod in [["asc", asc], ["desc", desc]]:
                if sortType == iSortType:
                    return query.order_by(orderMethod(merchantOrder))
        return query

    def paginate(self, query: Select, pageNo: int, limitPerPage: int) -> Select:
        """
        paginate query by defining page number and page limit
        """
        query = query.offset((pageNo - 1) * limitPerPage)
        query = query.limit(limitPerPage)
        return query

    async def execute_pagination(self, session: AsyncSession, query: Select) -> dict:
        """
        sort, filter and paginate the query with executed query outputs
        """
        query = self.filter(query)
        countAfterFilter = await session.execute(
            select(func.count()).select_from(query.subquery())
        )
        countAfterFilter = countAfterFilter.scalars().one()
        query = self.sort(query, self.getParams.sortBy, self.getParams.sortType)
        query = self.paginate(query, self.getParams.page, self.getParams.limit)
        query = await session.execute(query)
        datas = query.scalars().all()
        datas = self.filter_primary_key(datas)
        return create_response(
            data={"list": datas},
            meta={
                "page": self.getParams.page,
                "limit": self.getParams.limit,
                "total": countAfterFilter,
            },
            status=status.success(),
        )


class QueryPaginatorMultiple:
    def __init__(self, getParams: QueryPaginationParams, selector: Selector):
        self.rawQuery = selector.query
        self.getParams = getParams
        self.selector = selector
        if getParams.fields:
            self.fields = validate_field(
                self.selector.keys, getParams.fields.split(",")
            )
        else:
            self.fields = self.selector.keys

    def filter(self, data: list, fields: Optional[list] = None) -> Select:
        """
        filter the desired fields from the query (it will remains the primary key)
        """
        if not fields:
            fields = self.fields
        newData = []
        for d in data:
            newPair = {}
            for k in d:
                if k in fields:
                    newPair[k] = d[k]
            newData.append(newPair)
        return newData

    def sort(self, query: Select, sortBy: str, sortType: str) -> Select:
        """
        sort your query by defining both the sortBy 'fields' and sortType 'asc'/'desc' parameters
        """
        if sortBy in self.fields:
            merchantOrder = self.selector.columnsKeyPair[sortBy]
            for iSortType, orderMethod in [["asc", asc], ["desc", desc]]:
                if sortType == iSortType:
                    return query.order_by(orderMethod(merchantOrder))
        return query

    def paginate(self, query: Select, pageNo: int, limitPerPage: int) -> Select:
        """
        paginate query by defining page number and page limit
        """
        query = query.offset((pageNo - 1) * limitPerPage)
        query = query.limit(limitPerPage)
        return query

    async def execute_pagination(self, session: AsyncSession, query: Select):
        countAfterFilter = await session.execute(
            select(func.count()).select_from(query.subquery())
        )
        countAfterFilter = countAfterFilter.scalars().one()
        query = self.sort(query, self.getParams.sortBy, self.getParams.sortType)
        query = self.paginate(query, self.getParams.page, self.getParams.limit)
        datas = await self.selector.execute(session, query)
        datas = self.filter(datas)
        return create_response(
            data={"list": datas},
            meta={
                "page": self.getParams.page,
                "limit": self.getParams.limit,
                "total": countAfterFilter,
            },
            status=status.success(),
        )


class BaseWhereClause:
    def __init__(self, classModel, *whereExpression, **whereClause):
        self.classModel = classModel
        self.we = whereExpression
        self.wc = whereClause

    def applyWhereObject(self, query: Select, whereClauseDict: Optional[dict] = {}, **WhereClauseKwargs):
        WhereClauseKwargs.update(whereClauseDict)
        self.wc.update(WhereClauseKwargs)
        self.wc = self.filterEmptyClause(self.wc)
        for w in self.we:
            query = query.where(w)
        for key in self.wc:
            query = query.where(self.classModel.__dict__[key] == self.wc[key])
        return query
    
    def filterEmptyClause(self, whereClauseInDict: dict):
        newDict = {}
        for key, val in whereClauseInDict.items():
            if val != None:
                newDict[key] = val
        return newDict


class BaseCRUD:
    def __init__(self, classModel):
        self.classModel = classModel

    def where(self, *whereExpression, **whereClause):
        return BaseWhereClause(self.classModel, *whereExpression, **whereClause)
    
    def filter_update_value(self, pydanticModel, additionalKey):
        updates = {}
        updateValue = pydanticModel.dict()
        fields = [i for i in vars(self.classModel) if "_" not in [i[0], i[-1]]]
        for key in fields:
            if key in updateValue:
                if updateValue[key] != None:
                    updates[key] = updateValue[key]
            if key in additionalKey:
                updates[key] = additionalKey[key]
        return updates

    async def read(
            self,
            getParams: QueryPaginationParams,
            session: AsyncSession,
            whereClauseObject: Optional[BaseWhereClause] = None,
            **whereClause
        ):
        try:
            paginator = QueryPaginator(getParams, self.classModel)
            query = paginator.rawQuery
            if whereClauseObject:
                query = whereClauseObject.applyWhereObject(query, whereClause)
            return await paginator.execute_pagination(session, query)
        except Exception as e:
            logger.error(str(e))
            return create_response(status=status.error(e))

    async def create(self, pydanticModel, session: AsyncSession):
        try:
            newData = self.classModel(**pydanticModel.dict())
            session.add(newData)
            await session.commit()
            await session.refresh(newData)
            return create_response(status=status.success())
        except Exception as e:
            logger.error(str(e))
            return create_response(status=status.error(e))

    async def update(
        self,
        pydanticModel,
        id: Optional[int],
        session: AsyncSession,
        whereClauseObject: Optional[BaseWhereClause] = None,
        additionalKey: Optional[Dict[str, Any]] = [],
        **whereClause
    ):
        try:
            ## validate pydantic params
            if not any([v!=None for k,v in vars(pydanticModel).items() if "_" not in [k[0], k[-1]]]):
                return create_response(status=status.data_is_not_updated())

            ## check existed data
            query = select(self.classModel)
            if id != None:
                query = query.where(self.classModel.id == id)
            if whereClauseObject:
                query = whereClauseObject.applyWhereObject(query, whereClause)
            data = await session.execute(query)
            data = data.scalars().first()

            ## update data if exist
            if not data:
                return create_response(status=status.data_is_not_exist())
            else:
                query = update(self.classModel)
                if id != None:
                    query = query.where(self.classModel.id == id)
                if whereClauseObject:
                    query = whereClauseObject.applyWhereObject(query, whereClause)
                updateValues = self.filter_update_value(pydanticModel, additionalKey)
                query = query.values(**updateValues)
                await session.execute(query)
                await session.commit()
                return create_response(status=status.success())
        except Exception as e:
            logger.error(str(e))
            return create_response(status=status.error(e))

    async def delete(
        self,
        id: Optional[int],
        session: AsyncSession,
        whereClauseObject: Optional[BaseWhereClause] = None,
        **whereClause
    ):
        try:
            query = select(self.classModel)
            if id != None:
                query = query.where(self.classModel.id == id)
            if whereClauseObject:
                query = whereClauseObject.applyWhereObject(query, whereClause)
            data = await session.execute(query)
            data = data.scalars().all()
            if not data:
                return create_response(status=status.data_is_not_exist())
            else:
                for d in data:
                    await session.delete(d)
                await session.commit()
                return create_response(status=status.success())
        except Exception as e:
            logger.error(str(e))
            return create_response(status=status.error(e))
