# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table(u'md_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('mobile', self.gf('django.db.models.fields.CharField')(unique=True, max_length=11, db_index=True)),
        ))
        db.send_create_signal(u'md', ['User'])

        # Adding M2M table for field groups on 'User'
        m2m_table_name = db.shorten_name(u'md_user_groups')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'md.user'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'User'
        m2m_table_name = db.shorten_name(u'md_user_user_permissions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'md.user'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(m2m_table_name, ['user_id', 'permission_id'])


        # Changing field 'Message.user'
        db.alter_column(u'md_message', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['md.User']))

        # Changing field 'ActivityInvite.user'
        db.alter_column(u'md_activityinvite', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['md.User']))

        # Changing field 'ActivityInvite.refer'
        db.alter_column(u'md_activityinvite', 'refer_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['md.User']))

        # Changing field 'Chat.user'
        db.alter_column(u'md_chat', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['md.User']))

        # Changing field 'UserToken.user'
        db.alter_column(u'md_usertoken', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['md.User']))

        # Changing field 'Activity.owner'
        db.alter_column(u'md_activity', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['md.User']))

    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'md_user')

        # Removing M2M table for field groups on 'User'
        db.delete_table(db.shorten_name(u'md_user_groups'))

        # Removing M2M table for field user_permissions on 'User'
        db.delete_table(db.shorten_name(u'md_user_user_permissions'))


        # Changing field 'Message.user'
        db.alter_column(u'md_message', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']))

        # Changing field 'ActivityInvite.user'
        db.alter_column(u'md_activityinvite', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']))

        # Changing field 'ActivityInvite.refer'
        db.alter_column(u'md_activityinvite', 'refer_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']))

        # Changing field 'Chat.user'
        db.alter_column(u'md_chat', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']))

        # Changing field 'UserToken.user'
        db.alter_column(u'md_usertoken', 'user_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']))

        # Changing field 'Activity.owner'
        db.alter_column(u'md_activity', 'owner_id', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User']))

    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'md.activity': {
            'Meta': {'ordering': "['-create_at']", 'object_name': 'Activity'},
            'create_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'to': u"orm['md.User']"}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'update_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ManyToManyField', [], {'related_name': "'participate'", 'symmetrical': 'False', 'to': u"orm['md.User']"})
        },
        u'md.activityinvite': {
            'Meta': {'object_name': 'ActivityInvite'},
            'activity': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['md.Activity']"}),
            'avaiable': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'create_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'refer': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'related_name': "'refers'", 'to': u"orm['md.User']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'default': '0', 'related_name': "'users'", 'to': u"orm['md.User']"})
        },
        u'md.chat': {
            'Meta': {'ordering': "['-id']", 'object_name': 'Chat'},
            'activity': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['md.Activity']"}),
            'create_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '4000'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['md.User']"})
        },
        u'md.message': {
            'Meta': {'ordering': "['-create_at']", 'object_name': 'Message'},
            'activity': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['md.Activity']"}),
            'addons': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'body': ('django.db.models.fields.TextField', [], {}),
            'create_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39'}),
            'message_type': ('django.db.models.fields.CharField', [], {'default': "'Text'", 'max_length': '1'}),
            'stash': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'update_at': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['md.User']"})
        },
        u'md.messageaddon': {
            'Meta': {'object_name': 'MessageAddon'},
            'create_at': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2013, 6, 14, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'extra': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'message': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['md.Message']"}),
            'stash': ('django.db.models.fields.BooleanField', [], {'default': 'True'})
        },
        u'md.smslog': {
            'Meta': {'object_name': 'SMSLog'},
            'content': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'create_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39'}),
            'mobile': ('django.db.models.fields.TextField', [], {})
        },
        u'md.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'mobile': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '11', 'db_index': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'md.usertoken': {
            'Meta': {'object_name': 'UserToken'},
            'create_at': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.GenericIPAddressField', [], {'max_length': '39'}),
            'token': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['md.User']"})
        }
    }

    complete_apps = ['md']