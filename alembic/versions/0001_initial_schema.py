"""initial schema

Revision ID: 0001_initial
Revises: 
Create Date: 2025-10-23 00:00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('1')),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('license_key', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('preferences', sa.Text(), nullable=True),
        sa.UniqueConstraint('username', name='uq_users_username'),
        sa.UniqueConstraint('license_key', name='uq_users_license_key'),
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_username', 'users', ['username'])
    op.create_index('ix_users_license_key', 'users', ['license_key'])

    # rubrics
    op.create_table(
        'rubrics',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('discipline', sa.String(), nullable=False),
        sa.Column('regulation', sa.Text(), nullable=False),
        sa.Column('common_pitfalls', sa.Text(), nullable=False),
        sa.Column('best_practice', sa.Text(), nullable=False),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.UniqueConstraint('name', name='uq_rubrics_name'),
    )
    op.create_index('ix_rubrics_id', 'rubrics', ['id'])
    op.create_index('ix_rubrics_name', 'rubrics', ['name'])
    op.create_index('ix_rubrics_discipline', 'rubrics', ['discipline'])
    op.create_index('ix_rubrics_category', 'rubrics', ['category'])

    # reports
    op.create_table(
        'reports',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('document_name', sa.String(length=255), nullable=False),
        sa.Column('analysis_date', sa.DateTime(), nullable=True),
        sa.Column('compliance_score', sa.Float(), nullable=False),
        sa.Column('document_type', sa.String(), nullable=True),
        sa.Column('discipline', sa.String(), nullable=True),
        sa.Column('analysis_result', sa.Text(), nullable=False),
        sa.Column('document_embedding', sa.LargeBinary(), nullable=True),
    )
    op.create_index('ix_reports_id', 'reports', ['id'])
    op.create_index('ix_reports_document_name', 'reports', ['document_name'])
    op.create_index('ix_reports_analysis_date', 'reports', ['analysis_date'])
    op.create_index('ix_reports_compliance_score', 'reports', ['compliance_score'])
    op.create_index('ix_reports_document_type', 'reports', ['document_type'])
    op.create_index('ix_reports_discipline', 'reports', ['discipline'])

    # findings
    op.create_table(
        'findings',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('report_id', sa.Integer(), sa.ForeignKey('reports.id'), nullable=False),
        sa.Column('rule_id', sa.String(), nullable=False),
        sa.Column('risk', sa.String(), nullable=False),
        sa.Column('personalized_tip', sa.Text(), nullable=False),
        sa.Column('problematic_text', sa.Text(), nullable=False),
        sa.Column('confidence_score', sa.Float(), nullable=False, server_default=sa.text('0')),
    )
    op.create_index('ix_findings_id', 'findings', ['id'])
    op.create_index('ix_findings_report_id', 'findings', ['report_id'])
    op.create_index('ix_findings_rule_id', 'findings', ['rule_id'])
    op.create_index('ix_findings_risk', 'findings', ['risk'])

    # feedback_annotations
    op.create_table(
        'feedback_annotations',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('finding_id', sa.Integer(), sa.ForeignKey('findings.id'), nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('is_correct', sa.Boolean(), nullable=False),
        sa.Column('user_comment', sa.Text(), nullable=True),
        sa.Column('correction', sa.Text(), nullable=True),
        sa.Column('feedback_type', sa.String(), nullable=False, server_default=sa.text("'finding_accuracy'")),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_index('ix_feedback_annotations_id', 'feedback_annotations', ['id'])
    op.create_index('ix_feedback_annotations_finding_id', 'feedback_annotations', ['finding_id'])
    op.create_index('ix_feedback_annotations_user_id', 'feedback_annotations', ['user_id'])

    # habit_goals
    op.create_table(
        'habit_goals',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('habit_number', sa.Integer(), nullable=True),
        sa.Column('target_value', sa.Float(), nullable=True),
        sa.Column('current_value', sa.Float(), nullable=True, server_default=sa.text('0')),
        sa.Column('progress', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('status', sa.String(length=20), nullable=False, server_default=sa.text("'active'")),
        sa.Column('target_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_habit_goals_id', 'habit_goals', ['id'])
    op.create_index('ix_habit_goals_user_id', 'habit_goals', ['user_id'])

    # habit_achievements
    op.create_table(
        'habit_achievements',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('achievement_id', sa.String(length=100), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('icon', sa.String(length=10), nullable=False, server_default=sa.text("'??'")),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('earned_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_habit_achievements_id', 'habit_achievements', ['id'])
    op.create_index('ix_habit_achievements_user_id', 'habit_achievements', ['user_id'])
    op.create_index('ix_habit_achievements_achievement_id', 'habit_achievements', ['achievement_id'])

    # habit_progress_snapshots
    op.create_table(
        'habit_progress_snapshots',
        sa.Column('id', sa.Integer(), primary_key=True, nullable=False),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('snapshot_date', sa.Date(), nullable=False),
        sa.Column('habit_1_percentage', sa.Float(), nullable=False, server_default=sa.text('0')),
        sa.Column('habit_2_percentage', sa.Float(), nullable=False, server_default=sa.text('0')),
        sa.Column('habit_3_percentage', sa.Float(), nullable=False, server_default=sa.text('0')),
        sa.Column('habit_4_percentage', sa.Float(), nullable=False, server_default=sa.text('0')),
        sa.Column('habit_5_percentage', sa.Float(), nullable=False, server_default=sa.text('0')),
        sa.Column('habit_6_percentage', sa.Float(), nullable=False, server_default=sa.text('0')),
        sa.Column('habit_7_percentage', sa.Float(), nullable=False, server_default=sa.text('0')),
        sa.Column('total_findings', sa.Integer(), nullable=False, server_default=sa.text('0')),
        sa.Column('overall_progress_score', sa.Float(), nullable=False, server_default=sa.text('0')),
        sa.Column('consistency_score', sa.Float(), nullable=False, server_default=sa.text('0')),
        sa.Column('improvement_rate', sa.Float(), nullable=False, server_default=sa.text('0')),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_habit_progress_snapshots_id', 'habit_progress_snapshots', ['id'])
    op.create_index('ix_habit_progress_snapshots_user_id', 'habit_progress_snapshots', ['user_id'])
    op.create_index('ix_habit_progress_snapshots_snapshot_date', 'habit_progress_snapshots', ['snapshot_date'])


def downgrade() -> None:
    op.drop_table('habit_progress_snapshots')
    op.drop_table('habit_achievements')
    op.drop_table('habit_goals')
    op.drop_table('feedback_annotations')
    op.drop_table('findings')
    op.drop_table('reports')
    op.drop_table('rubrics')
    op.drop_table('users')

