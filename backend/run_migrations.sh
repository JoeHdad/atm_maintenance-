#!/bin/bash
# Post-deployment migration script for Render

set -e

echo "🔄 Running Django migrations..."
python manage.py migrate

echo "✅ Migrations completed successfully!"
echo ""
echo "📋 Next steps (run in Render shell):"
echo "   python manage.py createsuperuser"
echo "   python manage.py collectstatic --noinput"
