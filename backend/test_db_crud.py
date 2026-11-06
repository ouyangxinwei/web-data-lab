
"""临时测试：验证四张 ORM 表的关联及 CRUD 操作。"""
from uuid import uuid4

from sqlalchemy import select

from app.database import SessionLocal
from app.models import (
    DataSource,
    CollectionTask,
    CollectionRun,
    CollectedRecord,
)


def main():
    # 使用唯一名称，避免与已有数据冲突。
    test_name = f"WDL_TEST_{uuid4().hex[:8]}"

    try:
        # 一个事务中完成测试，任何异常都会自动回滚。
        with SessionLocal.begin() as db:

            # 1. INSERT：创建数据源。
            source = DataSource(
                name=test_name,
                source_type="api",
                base_url="https://example.com/api",
                config_json={"test": True},
            )
            db.add(source)
            db.flush()

            # 2. INSERT：创建采集任务。
            task = CollectionTask(
                source=source,
                name=f"{test_name}_TASK",
                schedule_type="manual",
                schedule_config={},
            )
            db.add(task)
            db.flush()

            # 3. INSERT：创建执行记录。
            run = CollectionRun(
                task=task,
                status="success",
                records_count=1,
            )
            db.add(run)
            db.flush()

            # 4. INSERT：创建采集结果。
            record = CollectedRecord(
                source=source,
                run=run,
                data_json={"message": "ORM test successful"},
            )
            db.add(record)
            db.flush()

            print("INSERT: 四张表的记录创建成功")

            # 5. SELECT：检查数据和关联。
            found = db.scalar(
                select(DataSource).where(DataSource.name == test_name)
            )
            assert found is not None
            assert found.tasks[0].id == task.id
            assert found.records[0].id == record.id
            assert task.source.id == source.id
            assert run.task.id == task.id
            assert record.run.id == run.id

            print("SELECT: 查询及 ORM 关联正常")

            # 6. UPDATE：更新数据源名称。
            source.name = f"{test_name}_UPDATED"
            db.flush()

            updated = db.scalar(
                select(DataSource).where(
                    DataSource.name == f"{test_name}_UPDATED"
                )
            )
            assert updated is not None

            print("UPDATE: 更新成功")

            # 7. DELETE：按外键依赖顺序删除。
            db.delete(record)
            db.delete(run)
            db.delete(task)
            db.delete(source)
            db.flush()

            print("DELETE: 删除成功")

        print("\n全部 ORM CRUD 测试通过！")
        print("测试记录已清理，事务已提交。")

    except Exception:
        print("\nORM 测试失败，事务已回滚。")
        raise


if __name__ == "__main__":
    main()
