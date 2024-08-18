import os

from requests import get
from dotenv import load_dotenv
from django.shortcuts import render
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.views.generic.base import ContextMixin
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator

from .forms import ReqForm, UserReqForm, AuthUserReqForm
from .models import Vacancy, Word, Wordskill, Area, Schedule
from hhapp.management.commands.full_db import Command


load_dotenv()


def start(request):
    title = 'главная страница'
    return render(request, 'hhapp/index.html', {'title': title})


def form(request):
    if not request.user.is_authenticated:
        form1 = UserReqForm()
    else:
        form1 = AuthUserReqForm(initial={'vacancy': request.user.text,
                                         'areas': request.user.areas.all(),
                                         'schedules': request.user.schedules.all()})
        title = 'страница формы'
    return render(request, 'hhapp/form.html', context={'form': form1, 'title': title})


def result(request):
    print('gist')
    if request.method == 'POST':
        print('='*70)
        print('post')
        form = UserReqForm(request.POST)
        if form.is_valid():
            vac = form.cleaned_data['vacancy']
            where = form.cleaned_data['where']
            pages = form.cleaned_data['pages']
            # print(request.POST.getlist('areas'), request.POST.getlist('schedules'))

            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            # areas = [Area.objects.filter(id=it).first() for it in request.POST.getlist('areas')]
            # schedules = [Schedule.objects.filter(id=it).first() for it in request.POST.getlist('schedules')]
            # # print(areas, schedules, sep='\n')
            #~~~~~~~~~~~~~~~~~~~~~~~~
            areas_ids = request.POST.getlist('areas')
            schedules_ids = request.POST.getlist('schedules')
            # Загрузка связанных объектов с помощью select_related
            areas = Area.objects.filter(id__in=areas_ids).prefetch_related('vacancies')
            schedules = Schedule.objects.filter(id__in=schedules_ids).prefetch_related('vacancies')
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            #~~~~~~~~~~~~~~~~~~~~~~~~
            com = Command(vac, pages, where, areas, schedules)
            com.handle()
            v = Word.objects.get(word=vac)
            s = Wordskill.objects.filter(id_word_id=v.id).order_by('-percent').all()

            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            #~~~~~~~~~~~~~~~~~~~~~~~~
            # vac = Vacancy.active_objects.filter(word_id=v,
            #                                     area__in=areas,
            #                                     schedule__in=schedules).order_by('published').all()
            # vac = Vacancy.active_objects.all()
            #~~~~~~~~~~~~~~~~~~~~~~~~
            # Используем select_related для загрузки связанных объектов
            # vac = Vacancy.active_objects.select_related('area', 'schedule')
            vac = Vacancy.active_objects.filter(word_id=v).select_related('area', 'schedule')
            #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            
            #~~~~~~~~~~~~~~~~~~~~~~~~
            print('-'*70)
            # print(vac, v, s, sep='\n')
            print(f'Word-v: {v}')
            # print(f'Wordskill-s: {s}')
            # print(f'Vacancy-vac: {vac}')
            print(f'Total vacancies: {vac.count()}')
            #~~~~~~~~~~~~~~~~~~~~~~~~
            print('-'*70)
            paginator = Paginator(vac, 10)
            # page_number = request.GET.get('page')
            page_number = request.GET.get('page', 1)  # Устанавливаем значение по умолчанию на 1
            # print(f'page_number:{page_number}')    
            page_obj = paginator.get_page(page_number)
            print(f'page_obj: len: {len(page_obj)}')    
            print('='*70)
            return render(request, 'hhapp/about.html', context={'word': v,
                                                                'skills': s,
                                                                'page_obj': page_obj})
            #~~~~~~~~~~~~~~~~~~~~~~~~
        else:
            page_number = request.GET.get('page')
            print('get', page_number)
            if page_number:
                vac = form.cleaned_data['vacancy']
                where = form.cleaned_data['where']
                pages = form.cleaned_data['pages']
                # print(request.POST.getlist('areas'), request.POST.getlist('schedules'))
                areas = [Area.objects.filter(id=it).first() for it in request.POST.getlist('areas')]
                schedules = [Schedule.objects.filter(id=it).first() for it in request.POST.getlist('schedules')]
                v = Word.objects.get(word=vac)
                s = Wordskill.objects.filter(id_word_id=v.id).all()
                vac = Vacancy.objects.filter(word_id=v, area__in=areas, schedule__in=schedules).order_by('published').all()
                paginator = Paginator(vac, 10)
                page_obj = paginator.get_page(page_number)
                return render(request, 'hhapp/about.html', context={'word': v,
                                                                    'skills': s,
                                                                    'page_obj': page_obj})
            else:
                form1 = UserReqForm()
                return render(request, 'hhapp/form.html', context={'form': form1})


class WSList(ListView):
    model = Wordskill
    template_name = 'hhapp/ws_list.html'


class AreaList(ListView):
    model = Area
    template_name = 'hhapp/area_list.html'
    paginate_by = 3

    def get_queryset(self):
        return Area.objects.order_by('name').all()


class AreaDetail(DetailView):
    model = Area
    template_name = 'hhapp/area_detail.html'


class AreaPostMixin(ContextMixin):
    def prepare_area(self, url, areas):
        for item in areas:
            # print(item)
            if item['areas'] is not None:
                url[item['name']] = item['id']
                # print(1)
                self.prepare_area(url, item['areas'])
            else:
                url[item['name']] = item['id']

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # def parce(self, area):
    #     # r = {'url': 'https://api.superjob.ru/2.0/vacancies/',
    #     #      'param': {'town': area,
    #     #                'period': 1},
    #     #      'header': {'X-Api-App-Id': os.getenv('key_super'),
    #     #                 'Authorization': 'Bearer r.000000010000001.example.access_token',
    #     #                 'Content-Type': 'application/x-www-form-urlencoded'}
    #     #      }
    #     self.hh, self.zarpl = dict(), dict()
    #     for url, d in (('https://api.hh.ru/areas', self.hh), ('https://api.zarplata.ru/areas', self.zarpl)):
    #         res = get(url).json()
    #         self.prepare_area(d, res)
    #     # res = get(r['url'], headers=r['header'], params=r['param']).json()
    #     return {'name': area, 'ind_hh': self.hh.get(area, 0),
    #             'ind_zarp': self.zarpl.get(area, 0)}#,
    #             # 'ind_super': res['objects'][0]['town']['id'] if res['objects'] else 0}
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def parce(self, area):
        # Инициализация словарей для хранения данных
        self.hh, self.zarpl = {}, {}

        # Словарь с URL-адресами API
        api_urls = {
            'hh': 'https://api.hh.ru/areas',
            'zarpl': 'https://api.zarplata.ru/areas'
        }

        # Запросы к API для получения областей
        for key, url in api_urls.items():
            res = get(url).json()
            self.prepare_area(self.hh if key == 'hh' else self.zarpl, res)

        # Возврат результатов
        return {
            'name': area,
            'ind_hh': self.hh.get(area, 0),
            'ind_zarp': self.zarpl.get(area, 0)
        }
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def post(self, request, *args, **kwargs):
        text = request.POST['name']
        print(text)
        new_index = self.parce(text)
        print(new_index)
        Area.objects.create(**new_index)
        return render(request, 'hhapp/area_list.html', context={'object_list': Area.objects.order_by('name').all()})


class AreaCreate(LoginRequiredMixin, CreateView, AreaPostMixin):
    model = Area
    fields = ['name']
    success_url = reverse_lazy('hh:area_list')
    template_name = 'hhapp/area_create.html'


class AreaUpdateView(UpdateView):
    model = Area
    fields = ['name']
    success_url = reverse_lazy('hhapp:area_list')
    template_name = 'hhapp/area_create.html'


class AreaDeleteView(DeleteView):
    model = Area
    success_url = reverse_lazy('hhapp:area_list')
    template_name = 'hhapp/area_delete_confirm.html'

