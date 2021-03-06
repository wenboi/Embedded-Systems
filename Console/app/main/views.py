from history_data import *
from notice_py import *
from app import get_logger, get_config
import math
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from app import utils
from app.models import CfgNotify
from app.main.forms import CfgNotifyForm
from . import main

logger = get_logger(__name__)
cfg = get_config()

# 通用列表查询
def common_list(DynamicModel, view):
    # 接收参数
    action = request.args.get('action')
    id = request.args.get('id')
    page = int(request.args.get('page')) if request.args.get('page') else 1
    length = int(request.args.get('length')) if request.args.get('length') else cfg.ITEMS_PER_PAGE

    # 删除操作
    if action == 'del' and id:
        try:
            DynamicModel.get(DynamicModel.id == id).delete_instance()
            flash('删除成功')
        except:
            flash('删除失败')

    # 查询列表
    query = DynamicModel.select()
    total_count = query.count()

    # 处理分页
    if page: query = query.paginate(page, length)

    dict = {'content': utils.query_to_list(query), 'total_count': total_count,
            'total_page': math.ceil(total_count / length), 'page': page, 'length': length}
    return render_template(view, form=dict, current_user=current_user)


# 通用单模型查询&新增&修改
def common_edit(DynamicModel, form, view):
    id = request.args.get('id', '')
    if id:
        # 查询
        model = DynamicModel.get(DynamicModel.id == id)
        if request.method == 'GET':
            utils.model_to_form(model, form)
        # 修改
        if request.method == 'POST':
            if form.validate_on_submit():
                utils.form_to_model(form, model)
                model.save()
                flash('修改成功')
            else:
                utils.flash_errors(form)
    else:
        # 新增
        if form.validate_on_submit():
            model = DynamicModel()
            utils.form_to_model(form, model)
            model.save()
            flash('保存成功')
        else:
            utils.flash_errors(form)
    return render_template(view, form=form, current_user=current_user)


# 根目录跳转
@main.route('/', methods=['GET'])
@login_required
def root():
    return redirect(url_for('main.index'))


# 首页
@main.route('/index', methods=['GET'])
@login_required
def index():
    return render_template('index.html', current_user=current_user)

# 当前数据
@main.route('/now',methods = ['GET'])
@login_required
def now():
    # day_time, accurate_time, tem_list, hum_list = now_index()
    # print(day_time, accurate_time, tem_list, hum_list)
    day_time = "2019-05-07"
    accurate_time = "14:49:28"
    # ['00:00', '02:00', '04:00', '06:00', '08:00', '10:00', '12:00', '14:00', '16:00', '18:00', '20:00', '22:00']
    tem_list = [18,19,18,20,22,24,24,25]
    hum_list = [50,48,57,60,54,53,55,57]
    return render_template('now.html',day_time = day_time, accurate_time = accurate_time, tem_list = tem_list, hum_list = hum_list)


# 当前数据
@main.route('/hist_day/<datatime>',methods = ['GET'])
@login_required
def hist_day(datatime):
    time_data, tem_list, hum_list = data_find(int(datatime))
    return render_template('hist_day.html',time_data = time_data,tem_list = tem_list,hum_list = hum_list)

# 历史数据
@main.route('/history',methods = ['GET'])
@login_required
def history():
    stble_six = select_table_six()
    stble_six_notice = select_table_notice_six(select_table_notice())
    table_all = select_all_data()
    return render_template('history.html',stble_six = stble_six,stble_six_notice = stble_six_notice,table_all = table_all)


# 预警通知
@main.route('/notice', methods=['GET', 'POST'])
@login_required
def notice():
    table_six = select_six_notice()
    all_table = select_all_notice()
    return render_template('notice.html',table_six = table_six,all_table = all_table)


# 通知方式配置
@main.route('/notifyedit', methods=['GET', 'POST'])
@login_required
def notifyedit():
    return common_edit(CfgNotify, CfgNotifyForm(), 'notifyedit.html')
