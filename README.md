# crawl_naver_map

- 네이버 지도에서 keyword(검색어) 검색 결과 나온 리스트의 '업체명', '연락처', '주소' 크롤링
- 셀레니움(Selenium) 이용

## pyinstaller 로 exe 만들기

- pyinstaller --onefile crawl_main.py

## 참고사항

1. 하루종일 테스트하면서 계속 날렸더니 어느순간부터 일정시간동안 크롤링이 안되는 현상이 발생함
   - 이런 경우, 크롬창을 닫고 다시 실행하는 과정을 여러번 반복했더니 해결됨 (하루종일 이 프로그램을 실행하는 일이 드물것으로 생각)
2. 데이터를 수집하는 과정이 결국 계속해서 api 요청을 보내는 형식이므로, 중간중간에 잠깐(몇십초) api요청이 안되는 현상 발생
   - 이런 경우, 같은 api요청에 대해서 최대 10번 시도를 해보고 안되면 그냥 넘어가는 방식으로 해결함(프로그램이 실행될때 어느 부분에서 에러가 발생했는지 로그로 확인 가능함)
   - 여러번 테스트 결과 10번 시도해도 안되는 경우는 거의 없었음
3. 크롤링을 하는 도중에 크롬창을 끄면 안됨
   - 크롬창을 끄면 크롤링이 멈추는 현상이 발생함
4. 검색어마다 고려해야되는 부분이 조금씩 다르기 때문에, 특정 검색어에서는 오류가 발생할 수 있음
   - 특히 '식당' 관련해서 검색시에는 웹구조 형식이 달라서 따로 처리를 해두었기 때문에, '식당' 검색시에는 속도가 더 느림
