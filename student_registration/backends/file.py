

def get_default_provider():
    from .providers.azure import Azure

    return Azure()

def store_file(data, file_name, params=None):

    from django.conf import settings
    from azure.storage import CloudStorageAccount

    file_name = '{}.{}'.format(file_name, settings.DEFAULT_FILE_FORMAT)

    storage_client = CloudStorageAccount(settings.AZURE_ACCOUNT_NAME,
                                         settings.AZURE_ACCOUNT_KEY)
    blob_service = storage_client.create_blob_service()

    blob_service.put_block_blob_from_bytes(
        settings.AZURE_CONTAINER,
        file_name,
        data,
        content_language=settings.DEFAULT_FILE_CONTENT_LANGUAGE,
        x_ms_blob_content_type=settings.DEFAULT_FILE_CONTENT_TYPE
    )

    file_link = blob_service.make_blob_url(settings.AZURE_CONTAINER, file_name)
    create_record(file_link, file_name, params)


def create_record(url, file_name, params):
    from .models import Exporter
    instance = Exporter.objects.create(name=file_name, file_url=url)
    if params and 'user' in params:
        instance.exported_by_id = int(params['user'])
    instance.save()


def send_email(url, file_name):
    from django.core.mail import send_mail
    send_mail(
        file_name+' extraction',
        url,
        'achamseddine@unicef.org',
        ['achamseddine@unicef.org'],
        fail_silently=False,
    )
