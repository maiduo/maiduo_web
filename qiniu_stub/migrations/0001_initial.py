# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Credential'
        db.create_table(u'qiniu_stub_credential', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('access', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('secret', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'qiniu_stub', ['Credential'])

        # Adding model 'Key'
        db.create_table(u'qiniu_stub_key', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('size', self.gf('django.db.models.fields.IntegerField')()),
            ('create_at', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'qiniu_stub', ['Key'])


    def backwards(self, orm):
        # Deleting model 'Credential'
        db.delete_table(u'qiniu_stub_credential')

        # Deleting model 'Key'
        db.delete_table(u'qiniu_stub_key')


    models = {
        u'qiniu_stub.credential': {
            'Meta': {'object_name': 'Credential'},
            'access': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'secret': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        u'qiniu_stub.key': {
            'Meta': {'object_name': 'Key'},
            'create_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'size': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['qiniu_stub']