from ..services import database as db
from app.core.dependencies import SessionDep
from loguru import logger
from icecream import ic
import xlwt
from xlwt import Workbook, XFStyle, Alignment, Font
async def get_file_raspisanie(session: SessionDep):
    try:
        logger.debug("Формирование запроса для бд выбор расписания для всех групп")
        query = (
            db.select(db.table.Lessons.group,
                      db.table.Lessons.item,
                      db.table.Lessons.num_day,
                      db.table.Lessons.num_lesson,
                      db.table.Lessons.week,
                      db.table.Lessons.teacher,
                      db.table.Lessons.cabinet,
                      )
            .filter(db.table.Lessons.num_lesson != 0) # убираем классный час из расписания
        )

        logger.debug("Выполняем запрос в бд")
        result = await session.execute(query)

        logger.debug("Получаем результат из бд")
        lessons_data = result.all()
                
        logger.debug("Распределяем расписание по дням")
        lessons_sorted = {}

        def process_lesson(lesson, week_key):
            group = lesson.group
            week = lessons_sorted.setdefault(group, {}).setdefault(week_key, {})
            for i in range(1, 7):
                day_key = "day_" + str(i)
                day = week.setdefault(day_key, {})
                if week_key == "week_1":
                    count_lessons = 5
                    if i == 6:
                        count_lessons = 4
                        
                    for b in range(1, count_lessons):
                        lesson_key = "lesson_" + str(b)
                        lesson_entry = day.setdefault(lesson_key, {
                            "item": "",
                            "teacher": "",
                            "cabinet": "",
                        })
                
            day_key = "day_" + str(lesson.num_day)
            day = week.setdefault(day_key, {})
            lesson_key = "lesson_" + str(lesson.num_lesson)
            lesson_entry = day.setdefault(lesson_key, {})
            
            lesson_entry.update({
                "item": lesson.item,
                "teacher": lesson.teacher.split()[0] if len(lesson.teacher.split()) == 3 else lesson.teacher,  # Оставляем только фамилию
                "cabinet": lesson.cabinet,
            })

        for lesson in lessons_data:
            if lesson.week == 1:
                process_lesson(lesson, "week_1")
            elif lesson.week == 2:
                process_lesson(lesson, "week_2")
        
       
        keys_coordinats = {
            'day_1': {
                'lesson_1': 1,
                'lesson_2': 3,
                'lesson_3': 5,
                'lesson_4': 7,
            },
            'day_2': {
                'lesson_1': 9,
                'lesson_2': 11,
                'lesson_3': 13,
                'lesson_4': 15,
            },
            'day_3': {
                'lesson_1': 17,
                'lesson_2': 19,
                'lesson_3': 21,
                'lesson_4': 23,
            },
            'day_4': {
                'lesson_1': 25,
                'lesson_2': 27,
                'lesson_3': 29,
                'lesson_4': 31,
            },
            'day_5': {
                'lesson_1': 33,
                'lesson_2': 35,
                'lesson_3': 37,
                'lesson_4': 39,
            },
            'day_6': {
                'lesson_1': 41,
                'lesson_2': 43,
                'lesson_3': 45,
                'lesson_4': 47,
            },
                
        }

        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('TDSheet')

        worksheet.col(0).width = 700
        worksheet.row(0).height = 400

        for i in range(1, 47):
            worksheet.row(i).height = 400

        header_day_style = xlwt.easyxf('align: rotation 90, vertical center; font: bold on, height 160; borders: bottom thin, left thin, right thin; pattern: pattern solid, fore_colour gold')
        header_group_style = xlwt.easyxf('align: horiz center, vertical center; font: bold on, height 160; borders: bottom thin, left thin, right thin; pattern: pattern solid, fore_colour gold')
        day_style = xlwt.easyxf('align: rotation 90, vertical center; font: bold on, height 160; borders: top thin, bottom thin, left thin, right thin;')
        num_lesson_style = xlwt.easyxf('align: horiz left, vert center; font: height 200; borders: top thin, bottom thin, left thin, right thin;')
        cabinet_lesson_style = xlwt.easyxf('align: horiz center, vert center; font: name Times New Roman, height 160; borders: top thin, bottom thin, left thin, right thin;  pattern: pattern solid, fore_colour yellow')

        empty_lesson = {
                        "item": "",
                        "teacher": "",
                        "cabinet": "",
            }


        def lesson_style(size_font = 12, left=True, top=True, right=True, bottom=True, white=True):
            height = size_font * 20
            
            border_left_line = "thin" if left else 0
            border_top_line = "thin" if top else 0
            border_right_line = "thin" if right else 0
            border_bottom_line = "thin" if bottom else 0
            
            white_background = "pattern: pattern solid, fore_colour white" if white else ""
            
            return xlwt.easyxf(f'align: horiz center, vert center; font: name Times New Roman, height {height}; borders: top {border_top_line}, bottom {border_bottom_line}, left {border_left_line}, right {border_right_line}; {white_background}')


        def create_left_info(column, start_row=0):
            # Write headers and merge cells for days
            worksheet.write(start_row, column, "День", header_day_style)
            worksheet.write(start_row, column + 1, "Интервал", header_group_style)
            days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
            row = start_row + 1
            worksheet.col(column).width = 700
            for day in days:
                if day != "Суббота":
                    worksheet.write_merge(row, row + 7, column, column, day, day_style)
                    row += 8
                else:
                    worksheet.write_merge(row, row + 5, column, column, day, day_style)
                    
            row = start_row + 1
            worksheet.col(column + 1).width = 2000
            for _ in days:
                numbers = 5 if _ != "Суббота" else 4
                for num in range(1, numbers):
                    worksheet.write_merge(row, row + 1, column + 1, column + 1, f"{num} пара", num_lesson_style)
                    row += 2
                    

        def insert_group_pars():
            count_group = 0
            
            column = 2
            for group in lessons_sorted:
                count_group += 1
                worksheet.col(column).width = 4500
                worksheet.col(column + 1).width = 1200
                # print(group)
                worksheet.write(0, column, group, header_group_style)
                worksheet.write(0, column + 1, "", header_group_style)
                for week in lessons_sorted[group]:
                    # print(week)
                    for day in lessons_sorted[group][week]:
                        # print(day)
                        for lesson in lessons_sorted[group][week][day]:
                            if week.split("_")[1] == "1":
                                if lessons_sorted[group]["week_2"][day].get(lesson, False) == False:
                                    style_lesson_insert = lesson_style(size_font=11, bottom=None)
                                    style_teacher_insert = lesson_style(size_font=11, top=None)
                                        
                                    worksheet.write(keys_coordinats[day][lesson], column, lessons_sorted[group][week][day][lesson]['item'], style_lesson_insert)
                                    worksheet.write(keys_coordinats[day][lesson] + 1, column, lessons_sorted[group][week][day][lesson]['teacher'], style_teacher_insert), 
                                    worksheet.write_merge(keys_coordinats[day][lesson], keys_coordinats[day][lesson] + 1, column + 1, column + 1, lessons_sorted[group][week][day][lesson]['cabinet'], cabinet_lesson_style)
                                
                                else:
                                    style_lesson_insert = lesson_style(size_font=8, white=False)
                                    if lessons_sorted[group]["week_1"][day].get(lesson) == empty_lesson:
                                        worksheet.write(keys_coordinats[day][lesson], column, "---", style_lesson_insert)
                                        worksheet.write(keys_coordinats[day][lesson], column + 1, "", cabinet_lesson_style)
                                        continue
                                    
                                    worksheet.write(keys_coordinats[day][lesson], column, f"{lessons_sorted[group][week][day][lesson]['item']} {lessons_sorted[group][week][day][lesson]['teacher']}", style_lesson_insert)
                                    worksheet.write(keys_coordinats[day][lesson], column + 1, lessons_sorted[group][week][day][lesson]['cabinet'], cabinet_lesson_style)
                            if week.split("_")[1] == "2":
                                style_lesson_insert = lesson_style(size_font=8, white=False)

                                worksheet.write(keys_coordinats[day][lesson] + 1, column, f"{lessons_sorted[group][week][day][lesson]['item']} {lessons_sorted[group][week][day][lesson]['teacher']}", style_lesson_insert)
                                worksheet.write(keys_coordinats[day][lesson] + 1, column + 1, lessons_sorted[group][week][day][lesson]['cabinet'], cabinet_lesson_style)
                                
                if count_group == 10:
                    column += 2
                    create_left_info(column)
                    count_group = 0

                column += 2
        create_left_info(0)
        insert_group_pars()

        # Save the workbook
        workbook.save('raspisanie.xls')
        
        return True

    except Exception:
        logger.exception(f"Произошла ошибка при формировании расписания")
        return False
    