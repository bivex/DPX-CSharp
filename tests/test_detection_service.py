"""Tests for DetectionService orchestrator and HTML report formatter."""

from __future__ import annotations

from pattern_detector.adapters.outbound.persistence.html_report_formatter import HtmlReportFormatter
from pattern_detector.application.detection_service import DetectionService


def test_scan_csharp_samples():
    service = DetectionService()
    report = service.scan("examples/csharp_samples")

    assert report.total_detections_count > 20
    assert report.scanned_files_count >= 3
    assert len(report.summary_by_category) >= 6


def test_html_report_formatter_generates_valid_hud():
    service = DetectionService()
    report = service.scan("examples/csharp_samples")

    formatter = HtmlReportFormatter()
    html_output = formatter.format(report)

    assert "<!DOCTYPE html>" in html_output
    assert "DPX Architecture HUD" in html_output
    assert "FINDINGS" in html_output
    assert "INSPECTOR DRAWER" in html_output or "AI Architect Actions" in html_output
