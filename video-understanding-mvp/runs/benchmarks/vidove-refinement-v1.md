# ViDove Refinement Benchmark v1

## Summary

ViDove refinement was re-validated manually on two Chinese samples after fixing the local adapter path handling.

### Overall judgment
- ViDove refinement is now runnable end-to-end in the local workspace setup.
- It produces clear transcript quality gains over raw Whisper-base output on both a Chinese news clip and a Bilibili tutorial clip.
- The main remaining bottleneck is not transcript cleanup quality; it is the downstream MVP summary/chapter logic, which is still simplistic.

## Case 1: Chinese news clip
- Sample: `samples/hkcnews_china_20210203_clip120.mp4`
- Run dir: `runs/test-refine-manual/hkcnews_china_20210203_clip120`
- Refinement status: `success`

### Representative corrections
- `未容產品` → `美容产品`
- `元鳥` → `原料`
- `至今臨海警方近日倒破` → `浙江临海警方近日捣毁`

### Notes
- Improvement is not just spelling cleanup; the refined transcript becomes substantially more readable and semantically grounded.
- Some segments are normalized into cleaner written Chinese, which is useful for later summarization but should still be watched for over-inference.

## Case 2: Bilibili tutorial clip
- Sample: `samples/bilibili/BV1Nb421H77B_p1_clip300.mkv`
- Run dir: `runs/test-bili-tutorial-refine/BV1Nb421H77B_p1_clip300`
- Refinement status: `success`

### Representative corrections
- `短期视频` → `本期视频`
- `请问门先给个三连吗` → `请问能先给个三连吗`
- `言言下日来` → `炎炎夏日来临`

### Notes
- This confirms the gain transfers beyond the news clip and into a realistic Bilibili tutorial scenario.
- Refinement also improves segmentation and removes some malformed filler content.
- In a few places the refined transcript appears more selective or compressed than the raw transcript, so recall vs readability should be evaluated later.

## Practical conclusion
- Keep the current architecture direction: MVP skeleton + ViDove refinement.
- Use ViDove refinement as the current text cleanup layer for Chinese Bilibili understanding experiments.
- Next high-value work:
  1. formalize benchmark recording
  2. compare raw/refined summary quality more explicitly
  3. improve summary/chapter generation beyond the current template-style MVP output
