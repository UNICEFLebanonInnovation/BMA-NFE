# coding: utf-8
import django_tables2 as tables
from django.utils.translation import gettext as _

from .models import CLM, BLN, ABLN, RS, CBECE, GeneralQuestionnaire, Outreach, Bridging


class CommonTable(tables.Table):

    # edit_column = tables.TemplateColumn(verbose_name=_('Edit student'),
    #                                     template_name='django_tables2/edit_column.html',
    #                                     attrs={'url': ''})
    # delete_column = tables.TemplateColumn(verbose_name=_('Delete student'),
    #                                       template_name='django_tables2/delete_column.html',
    #                                       attrs={'url': ''})

    student_age = tables.Column(verbose_name=_('Age'), accessor='student.age')
    student_birthday = tables.Column(verbose_name=_('Birthday'), accessor='student.birthday')

    class Meta:
        model = CLM
        template = 'django_tables2/bootstrap.html'
        attrs = {'class': 'table table-bordered table-striped table-hover'}
        fields = (
            # 'edit_column',
            # 'delete_column',
        )


class BLNTable(CommonTable):

    edit_column = tables.TemplateColumn(verbose_name=_('Edit student'), orderable=False,
                                        template_name='django_tables2/clm_edit_column.html',
                                        attrs={'url': '/clm/bln-edit/', 'programme': 'BLN'})
    delete_column = tables.TemplateColumn(verbose_name=_('Delete student'), orderable=False,
                                          template_name='django_tables2/clm_delete_column.html',
                                          attrs={'url': '/api/clm-bln/', 'programme': 'BLN'})

    # monitoring_column = tables.TemplateColumn(verbose_name=_('monitoring'), orderable=False,
    #                                         template_name='django_tables2/clm_monitoring_column.html',
    #                                         attrs={'url': '/clm/bln-monitoring-questioner/', 'programme': 'BLN'})
    # referral_column = tables.TemplateColumn(verbose_name=_('refer'), orderable=False,
    #                                         template_name='django_tables2/clm_referral_column.html',
    #                                         attrs={'url': '/clm/bln-referral/', 'programme': 'BLN'})
    # followup_column = tables.TemplateColumn(verbose_name=_('Follow-up'), orderable=False,
    #                                         template_name='django_tables2/clm_followup_column.html',
    #                                         attrs={'url': '/clm/bln-followup/', 'programme': 'BLN'})
    # re_enroll_column = tables.TemplateColumn(verbose_name=_('Re-enroll'), orderable=False,
    #                                          template_name='django_tables2/clm_re_enroll_column.html',
    #                                          attrs={'url': '/clm/bln-add/', 'programme': 'BLN'})
    post_assessment_column = tables.TemplateColumn(verbose_name=_('Post-Assessment'), orderable=False,
                                                   template_name='django_tables2/clm_assessment_column.html',
                                                   attrs={'url': '/clm/bln-post-assessment/', 'programme': 'BLN'})
    fc_arabic_column = tables.TemplateColumn(verbose_name=_('Arabic'), orderable=False,
                                                   template_name='django_tables2/clm_fc_arabic_column.html',
                                                   attrs={'url': '/clm/bln-fc-add/', 'programme': 'BLN'})
    fc_math_column = tables.TemplateColumn(verbose_name=_('Math'), orderable=False,
                                                   template_name='django_tables2/clm_fc_math_column.html',
                                                   attrs={'url': '/clm/bln-fc-add/', 'programme': 'BLN'})
    fc_language_column = tables.TemplateColumn(verbose_name=_('Foreign Language'), orderable=False,
                                                   template_name='django_tables2/clm_fc_language_column.html',
                                                   attrs={'url': '/clm/bln-fc-add/', 'programme': 'BLN'})

    arabic_improvement = tables.Column(verbose_name=_('Arabic Language Development - Improvement'), orderable=False,
                                       accessor='arabic_improvement')
    foreign_language_improvement = tables.Column(verbose_name=_('Foreign Language Development - Improvement'), orderable=False,
                                                 accessor='foreign_language_improvement')
    math_improvement = tables.Column(verbose_name=_('Cognitive Development - Mathematics - Improvement'), orderable=False,
                                     accessor='math_improvement')
    social_emotional_improvement = tables.Column(verbose_name=_('Social-Emotional Development - Improvement'), orderable=False,
                                       accessor='arabic_improvement')
    psychomotor_improvement = tables.Column(verbose_name=_('Psychomotor Development for children with special needs - Improvement'),
                                       orderable=False, accessor='arabic_improvement')
    artistic_improvement = tables.Column(verbose_name=_('Artistic Development - Improvement'), orderable=False,
                                       accessor='arabic_improvement')

    assessment_improvement = tables.Column(verbose_name=_('Assessment Result - Improvement'), orderable=False,
                                           accessor='assessment_improvement')

    class Meta:
        model = BLN
        fields = (
            'edit_column',
            'delete_column',
            'post_assessment_column',
            'fc_arabic_column',
            'fc_language_column',
            'fc_math_column',
            # 'monitoring_column',
            # 'referral_column',
            # 'followup_column',
            # 're_enroll_column',
            'first_attendance_date',
            'round',
            # 'cycle',
            'governorate',
            'district',
            'internal_number',
            # 'student.id_number',
            'student.number',
            'student.first_name',
            'student.father_name',
            'student.last_name',
            'student.sex',
            'student_age',
            'student_birthday',
            'student.nationality',
            'student.mother_fullname',
            'arabic_improvement',
            'foreign_language_improvement',
            'math_improvement',
            'social_emotional_improvement',
            'psychomotor_improvement',
            'artistic_improvement',
            'assessment_improvement',
            'unsuccessful_pretest_reason',
            'unsuccessful_posttest_reason',
            'participation',
            'learning_result',
            'owner',
            'modified_by',
            'created',
            'modified',
            'comments',
        )


class ABLNTable(CommonTable):

    edit_column = tables.TemplateColumn(verbose_name=_('Edit student'), orderable=False,
                                        template_name='django_tables2/clm_edit_column.html',
                                        attrs={'url': '/clm/abln-edit/', 'programme': 'ABLN'})
    delete_column = tables.TemplateColumn(verbose_name=_('Delete student'), orderable=False,
                                          template_name='django_tables2/clm_delete_column.html',
                                          attrs={'url': '/api/clm-abln/', 'programme': 'ABLN'})

    # monitoring_column = tables.TemplateColumn(verbose_name=_('monitoring'), orderable=False,
    #                                         template_name='django_tables2/clm_monitoring_column.html',
    #                                         attrs={'url': '/clm/abln-monitoring-questioner/', 'programme': 'ABLN'})
    # referral_column = tables.TemplateColumn(verbose_name=_('refer'), orderable=False,
    #                                         template_name='django_tables2/clm_referral_column.html',
    #                                         attrs={'url': '/clm/abln-referral/', 'programme': 'ABLN'})
    # followup_column = tables.TemplateColumn(verbose_name=_('Follow-up'), orderable=False,
    #                                         template_name='django_tables2/clm_followup_column.html',
    #                                         attrs={'url': '/clm/abln-followup/', 'programme': 'ABLN'})
    post_assessment_column = tables.TemplateColumn(verbose_name=_('Post-Assessment'), orderable=False,
                                                   template_name='django_tables2/clm_assessment_column.html',
                                                   attrs={'url': '/clm/abln-post-assessment/', 'programme': 'ABLN'})
    fc_arabic_column = tables.TemplateColumn(verbose_name=_('Arabic'), orderable=False,
                                                   template_name='django_tables2/clm_fc_arabic_column.html',
                                                   attrs={'url': '/clm/abln-fc-add/', 'programme': 'ABLN'})
    fc_math_column = tables.TemplateColumn(verbose_name=_('Math'), orderable=False,
                                                   template_name='django_tables2/clm_fc_math_column.html',
                                                   attrs={'url': '/clm/abln-fc-add/', 'programme': 'ABLN'})
    arabic_improvement = tables.Column(verbose_name=_('Arabic Language Development - Improvement'), orderable=False,
                                       accessor='arabic_improvement')
    math_improvement = tables.Column(verbose_name=_('Cognitive Development - Mathematics - Improvement'), orderable=False,
                                     accessor='math_improvement')
    social_emotional_improvement = tables.Column(verbose_name=_('Social-Emotional Development - Improvement'), orderable=False,
                                       accessor='arabic_improvement')
    psychomotor_improvement = tables.Column(verbose_name=_('Psychomotor Development for children with special needs - Improvement'),
                                       orderable=False, accessor='arabic_improvement')
    artistic_improvement = tables.Column(verbose_name=_('Artistic Development - Improvement'), orderable=False,
                                       accessor='arabic_improvement')

    assessment_improvement = tables.Column(verbose_name=_('Assessment Result - Improvement'), orderable=False,
                                           accessor='assessment_improvement')

    class Meta:
        model = ABLN
        fields = (
            'edit_column',
            'delete_column',
            'post_assessment_column',
            'fc_arabic_column',
            'fc_math_column',
            'first_attendance_date',
            'round',
            # 'cycle',
            'governorate',
            'district',
            'internal_number',
            # 'student.id_number',
            'student.number',
            'student.first_name',
            'student.father_name',
            'student.last_name',
            'student.sex',
            'student_age',
            'student_birthday',
            'student.nationality',
            'student.mother_fullname',
            'arabic_improvement',
            'math_improvement',
            'social_emotional_improvement',
            'psychomotor_improvement',
            'artistic_improvement',
            'assessment_improvement',
            'unsuccessful_pretest_reason',
            'unsuccessful_posttest_reason',
            'participation',
            'learning_result',
            'owner',
            'modified_by',
            'created',
            'modified',
            'comments',
        )


class RSTable(CommonTable):

    edit_column = tables.TemplateColumn(verbose_name=_('Edit student'), orderable=False,
                                        template_name='django_tables2/clm_edit_column.html',
                                        attrs={'url': '/clm/rs-edit/', 'programme': 'RS'})
    delete_column = tables.TemplateColumn(verbose_name=_('Delete student'), orderable=False,
                                          template_name='django_tables2/clm_delete_column.html',
                                          attrs={'url': '/api/clm-rs/', 'programme': 'RS'})
    # delete_column = tables.TemplateColumn(verbose_name=_('Delete student'),
    #                                       template_name='django_tables2/delete_column.html',
    #                                       attrs={'url': '/api/clm-rs/', 'programme': 'RS'})
    # monitoring_column = tables.TemplateColumn(verbose_name=_('monitoring'), orderable=False,
    #                                         template_name='django_tables2/clm_monitoring_column.html',
    #                                         attrs={'url': '/clm/rs-monitoring-questioner/', 'programme': 'RS'})
    # referral_column = tables.TemplateColumn(verbose_name=_('refer'), orderable=False,
    #                                         template_name='django_tables2/clm_referral_column.html',
    #                                         attrs={'url': '/clm/rs-referral/', 'programme': 'RS'})
    # followup_column = tables.TemplateColumn(verbose_name=_('Follow-up'), orderable=False,
    #                                         template_name='django_tables2/clm_followup_column.html',
    #                                         attrs={'url': '/clm/rs-followup/', 'programme': 'RS'})

    post_assessment_column = tables.TemplateColumn(verbose_name=_('Post-Assessment'), orderable=False,
                                                   template_name='django_tables2/clm_assessment_column.html',
                                                   attrs={'url': '/clm/rs-post-assessment/', 'programme': 'RS'})
    fc_arabic_column = tables.TemplateColumn(verbose_name=_('Arabic'), orderable=False,
                                                   template_name='django_tables2/clm_fc_arabic_column.html',
                                                   attrs={'url': '/clm/rs-fc-add/', 'programme': 'RS'})
    fc_math_column = tables.TemplateColumn(verbose_name=_('Math'), orderable=False,
                                                   template_name='django_tables2/clm_fc_math_column.html',
                                                   attrs={'url': '/clm/rs-fc-add/', 'programme': 'RS'})
    fc_language_column = tables.TemplateColumn(verbose_name=_('Foreign Language'), orderable=False,
                                                   template_name='django_tables2/clm_fc_language_column.html',
                                                   attrs={'url': '/clm/rs-fc-add/', 'programme': 'RS'})
    fc_science_column = tables.TemplateColumn(verbose_name=_('Science'), orderable=False,
                                                   template_name='django_tables2/clm_fc_science_column.html',
                                                   attrs={'url': '/clm/rs-fc-add/', 'programme': 'RS'})

    fc_chemistry_column = tables.TemplateColumn(verbose_name=_('Chemistry'), orderable=False,
                                                  template_name='django_tables2/clm_fc_chemistry_column.html',
                                                  attrs={'url': '/clm/rs-fc-add/', 'programme': 'RS'})

    fc_physics_column = tables.TemplateColumn(verbose_name=_('Physics'), orderable=False,
                                                  template_name='django_tables2/clm_fc_physics_column.html',
                                                  attrs={'url': '/clm/rs-fc-add/', 'programme': 'RS'})

    pre_assessment_result = tables.Column(verbose_name=_('Assessment Result - Pre'), orderable=False,
                                          accessor='pre_test_score')
    post_assessment_result = tables.Column(verbose_name=_('Assessment Result - Post'), orderable=False,
                                           accessor='post_test_score')

    # assessment_improvement = tables.Column(verbose_name=_('Assessment Result - Improvement'), orderable=False,
    #                                        accessor='assessment_improvement')
    #
    # art_improvement = tables.Column(verbose_name=_('Language Development - Improvement'), orderable=False,
    #                                 accessor='art_improvement')
    # cognitive_improvement = tables.Column(verbose_name=_('Cognitive Development - Mathematics - Improvement'), orderable=False,
    #                                     accessor='cognitive_improvement')
    # science_improvement = tables.Column(verbose_name=_('Cognitive Development - Science - Improvement'), orderable=False,
    #                                     accessor='science_improvement')
    # social_improvement = tables.Column(verbose_name=_('Social-Emotional Development - Improvement'), orderable=False,
    #                                    accessor='social_improvement')
    # psycho_improvement = tables.Column(verbose_name=_('Psychomotor Development - Improvement'), orderable=False,
    #                                    accessor='psycho_improvement')
    # artistic_improvement = tables.Column(verbose_name=_('Artistic Development - Improvement'), orderable=False,
    #                                      accessor='artistic_improvement')

    class Meta:
        model = RS
        fields = (
            'edit_column',
            # 'referral_column',
            # 'followup_column',
            'delete_column',
            'post_assessment_column',
            'fc_arabic_column',
            'fc_language_column',
            'fc_math_column',
            'fc_science_column' ,
            'fc_chemistry_column' ,
            'fc_physics_column',
            'first_attendance_date',
            'round',
            'cycle',
            'site',
            'school',
            'governorate',
            'district',
            'internal_number',
            # 'student.id_number',
            'student.number',
            'student.first_name',
            'student.father_name',
            'student.last_name',
            'student.sex',
            'student_age',
            'student_birthday',
            'student.nationality',
            'student.mother_fullname',
            'pre_assessment_result',
            'post_assessment_result',
            # 'assessment_improvement',
            # 'art_improvement',
            # 'science_improvement',
            # 'cognitive_improvement',
            # 'social_improvement',
            # 'psycho_improvement',
            # 'artistic_improvement',
            'final_grade',
            'unsuccessful_pretest_reason',
            'unsuccessful_posttest_reason',
            'participation',
            'learning_result',
            'owner',
            'modified_by',
            'created',
            'modified',
            'comments',
        )


class CBECETable(CommonTable):

    edit_column = tables.TemplateColumn(verbose_name=_('Edit student'), orderable=False,
                                        template_name='django_tables2/clm_edit_column.html',
                                        attrs={'url': '/clm/cbece-edit/', 'programme': 'CBECE'})
    delete_column = tables.TemplateColumn(verbose_name=_('Delete student'), orderable=False,
                                          template_name='django_tables2/clm_delete_column.html',
                                          attrs={'url': '/api/clm-cbece/', 'programme': 'CBECE'})
    # monitoring_column = tables.TemplateColumn(verbose_name=_('monitoring'), orderable=False,
    #                                         template_name='django_tables2/clm_monitoring_column.html',
    #                                         attrs={'url': '/clm/cbece-monitoring-questioner/', 'programme': 'CBECE'})
    # referral_column = tables.TemplateColumn(verbose_name=_('refer'), orderable=False,
    #                                         template_name='django_tables2/clm_referral_column.html',
    #                                         attrs={'url': '/clm/cbece-referral/', 'programme': 'CBECE'})
    # followup_column = tables.TemplateColumn(verbose_name=_('Follow-up'), orderable=False,
    #                                         template_name='django_tables2/clm_followup_column.html',
    #                                         attrs={'url': '/clm/cbece-followup/', 'programme': 'CBECE'})

    post_assessment_column = tables.TemplateColumn(verbose_name=_('Post-Assessment'), orderable=False,
                                                   template_name='django_tables2/clm_assessment_column.html',
                                                   attrs={'url': '/clm/cbece-post-assessment/', 'programme': 'CBECE'})

    mid_assessment_column = tables.TemplateColumn(verbose_name=_('Mid-Assessment'), orderable=False,
                                                   template_name='django_tables2/clm_mid_assessment_column.html',
                                                   attrs={'url': '/clm/cbece-mid-assessment/', 'programme': 'CBECE'})

    fc_arabic_column = tables.TemplateColumn(verbose_name=_('Arabic'), orderable=False,
                                                   template_name='django_tables2/clm_fc_arabic_column.html',
                                                   attrs={'url': '/clm/cbece-fc-add/', 'programme': 'CBECE'})

    fc_math_column = tables.TemplateColumn(verbose_name=_('Math'), orderable=False,
                                                   template_name='django_tables2/clm_fc_math_column.html',
                                                   attrs={'url': '/clm/cbece-fc-add/', 'programme': 'CBECE'})

    fc_language_column = tables.TemplateColumn(verbose_name=_('Foreign Language'), orderable=False,
                                                   template_name='django_tables2/clm_fc_language_column.html',
                                                   attrs={'url': '/clm/cbece-fc-add/', 'programme': 'CBECE'})

    pre_assessment_result = tables.Column(verbose_name=_('Assessment Result - Pre'), orderable=False,
                                          accessor='pre_test_score')
    post_assessment_result = tables.Column(verbose_name=_('Assessment Result - Post'), orderable=False,
                                           accessor='post_test_score')

    assessment_improvement = tables.Column(verbose_name=_('Assessment Result - Improvement'), orderable=False,
                                           accessor='assessment_improvement')

    art_improvement = tables.Column(verbose_name=_('Language Development - Improvement'), orderable=False,
                                    accessor='art_improvement')
    cognitive_improvement = tables.Column(verbose_name=_('Cognitive Development - Mathematics - Improvement'), orderable=False,
                                        accessor='cognitive_improvement')
    science_improvement = tables.Column(verbose_name=_('Cognitive Development - Science - Improvement'), orderable=False,
                                        accessor='science_improvement')
    social_improvement = tables.Column(verbose_name=_('Social-Emotional Development - Improvement'), orderable=False,
                                       accessor='social_improvement')
    psycho_improvement = tables.Column(verbose_name=_('Psychomotor Development - Improvement'), orderable=False,
                                       accessor='psycho_improvement')
    artistic_improvement = tables.Column(verbose_name=_('Artistic Development - Improvement'), orderable=False,
                                         accessor='artistic_improvement')

    class Meta:
        model = CBECE
        fields = (
            'edit_column',
            # 'referral_column',
            # 'followup_column',
            'delete_column',
            'post_assessment_column',
            'mid_assessment_column',
            'fc_arabic_column',
            'fc_language_column',
            'fc_math_column',
            # 'monitoring_column',
            'first_attendance_date',
            'round',
            'cycle',
            'site',
            'school',
            'governorate',
            'district',
            'internal_number',
            # 'student.id_number',
            'student.number',
            'student.first_name',
            'student.father_name',
            'student.last_name',
            'student.sex',
            'student_age',
            'student_birthday',
            'student.nationality',
            'student.mother_fullname',
            'pre_assessment_result',
            'post_assessment_result',
            'assessment_improvement',
            'art_improvement',
            'science_improvement',
            'cognitive_improvement',
            'social_improvement',
            'psycho_improvement',
            'artistic_improvement',
            'final_grade',
            'unsuccessful_pretest_reason',
            'unsuccessful_posttest_reason',
            'participation',
            'learning_result',
            'owner',
            'modified_by',
            'created',
            'modified',
            'comments',
        )


class GeneralQuestionnaireTable(CommonTable):
    edit_column = tables.TemplateColumn(verbose_name=_('Edit Questionnaire'), orderable=False,
                                        template_name='django_tables2/clm_edit_column.html',
                                        attrs={'url': '/clm/general-questionnaire-edit/',
                                               'programme': 'General_Questionnaire'})
    delete_column = tables.TemplateColumn(verbose_name=_('Delete Questionnaire'), orderable=False,
                                          template_name='django_tables2/clm_delete_column.html',
                                          attrs={'url': '/api/general-questionnaire/',
                                                 'programme': 'General_Questionnaire'})

    class Meta:
        model = GeneralQuestionnaire
        fields = (
            'edit_column',
            'delete_column',
            'facilitator_full_name',
            'owner',
            'modified_by',
            'created',
            'modified',
        )


class OutreachTable(CommonTable):
    edit_column = tables.TemplateColumn(verbose_name=_('Edit student'), orderable=False,
                                        template_name='django_tables2/clm_edit_column.html',
                                        attrs={'url': '/clm/outreach-edit/', 'programme': 'Outreach'})
    delete_column = tables.TemplateColumn(verbose_name=_('Delete student'), orderable=False,
                                          template_name='django_tables2/clm_delete_column.html',
                                          attrs={'url': '/api/clm-outreach/', 'programme': 'Outreach'})

    class Meta:
        model = Outreach
        fields = (
            'edit_column',
            'delete_column',
            'internal_number',
            'student.number',
            'student.first_name',
            'student.father_name',
            'student.last_name',
            'student.sex',
            'student_age',
            'student_birthday',
            'student.nationality',
            'student.mother_fullname',
            'owner',
            'modified_by',
            'created',
            'modified',
            'comments',
        )


class BridgingTable(CommonTable):

    action_column = tables.TemplateColumn(verbose_name=_('Actions'), orderable=False,
                                        template_name='django_tables2/clm_action_column.html',
                                        attrs={'url_edit': '/clm/bridging-edit/',
                                               'url_delete': '/clm/bridging-delete/',
                                               'url_post_assessment': '/clm/bridging-post-assessment/',
                                               'url_mid_assessment1': '/clm/bridging-mid-assessment/',
                                               'url_mid_assessment2': '/clm/bridging-mid-assessment/',
                                               'url_followup': '/clm/bridging-followup/',
                                               'url_service': '/clm/bridging-service/',
                                               'programme': 'Bridging'})

    clm_absence_column = tables.TemplateColumn(verbose_name=_('Absence'), orderable=False,
                                                    template_name='django_tables2/clm_absence_column.html')

    clm_max_consecutive_column = tables.TemplateColumn(verbose_name=_('Max Consecutive'), orderable=False,
                                               template_name='django_tables2/clm_max_consecutive_column.html')

    class Meta:
        model = Bridging
        fields = (
            'action_column',
            'clm_absence_column',
            'clm_max_consecutive_column',
            'school.name',
            'registration_level',
            'round',
            'governorate',
            'district',
            'internal_number',
            'student.number',
            'student.unicef_id',
            'student.first_name',
            'student.father_name',
            'student.last_name',
            'student.sex',
            'student_age',
            'student_birthday',
            'student.nationality',
            'student.mother_fullname',
            'owner',
            'modified_by',
            'created',
            'modified',
        )

