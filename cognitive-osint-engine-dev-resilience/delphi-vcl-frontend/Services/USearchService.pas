unit USearchService;

interface

uses
  System.SysUtils;

type
  ESearchServiceError = class(Exception);

  TSearchCreateResult = record
    Message: string;
    SearchHistoryId: Integer;
  end;

  TScanStartResult = record
    Status: string;
    Message: string;
  end;

  TSearchService = class
  public
    function CreateSearch(const AQuery, ABearerToken: string): TSearchCreateResult;
    function StartScan(const AQuery: string; const ASearchHistoryId: Integer): TScanStartResult;
  end;

implementation

uses
  System.JSON,
  System.NetEncoding,
  System.Net.HttpClient,
  UHttpApiClient;

function TSearchService.CreateSearch(const AQuery, ABearerToken: string): TSearchCreateResult;
var
  LClient: THttpApiClient;
  LBody: TJSONObject;
  LResponse: IHTTPResponse;
  LJsonValue: TJSONValue;
  LMessageValue: TJSONValue;
  LIdValue: TJSONValue;
begin
  if Trim(AQuery) = '' then
    raise ESearchServiceError.Create('Arama metni bos olamaz.');

  if Trim(ABearerToken) = '' then
    raise ESearchServiceError.Create('JWT token bulunamadi.');

  LClient := THttpApiClient.Create;
  try
    LBody := TJSONObject.Create;
    try
      LBody.AddPair('query', AQuery);
      LResponse := LClient.PostJson('/api/v1/search', LBody, ABearerToken);
    finally
      LBody.Free;
    end;

    if (LResponse.StatusCode < 200) or (LResponse.StatusCode >= 300) then
      raise ESearchServiceError.CreateFmt('Search basarisiz. HTTP %d', [LResponse.StatusCode]);

    LJsonValue := TJSONObject.ParseJSONValue(LResponse.ContentAsString(TEncoding.UTF8));
    try
      if not (LJsonValue is TJSONObject) then
        raise ESearchServiceError.Create('Sunucu yaniti gecersiz.');

      LMessageValue := TJSONObject(LJsonValue).GetValue('message');
      LIdValue := TJSONObject(LJsonValue).GetValue('search_history_id');

      if Assigned(LMessageValue) then
        Result.Message := Trim(LMessageValue.Value)
      else
        Result.Message := '';

      if not Assigned(LIdValue) then
        raise ESearchServiceError.Create('search_history_id alani bulunamadi.');

      if LIdValue is TJSONNumber then
        Result.SearchHistoryId := TJSONNumber(LIdValue).AsInt
      else
        Result.SearchHistoryId := StrToIntDef(Trim(LIdValue.Value), -1);

      if Result.SearchHistoryId < 0 then
        raise ESearchServiceError.Create('search_history_id gecersiz.');
    finally
      LJsonValue.Free;
    end;
  finally
    LClient.Free;
  end;
end;

function TSearchService.StartScan(const AQuery: string; const ASearchHistoryId: Integer): TScanStartResult;
var
  LClient: THttpApiClient;
  LResponse: IHTTPResponse;
  LJsonValue: TJSONValue;
  LStatusValue: TJSONValue;
  LMessageValue: TJSONValue;
  LPath: string;
begin
  if Trim(AQuery) = '' then
    raise ESearchServiceError.Create('Arama metni bos olamaz.');

  if ASearchHistoryId <= 0 then
    raise ESearchServiceError.Create('search_history_id gecersiz.');

  LPath := '/api/v1/companies/scan?query=' + TNetEncoding.URL.Encode(AQuery) +
    '&search_history_id=' + IntToStr(ASearchHistoryId);

  LClient := THttpApiClient.Create;
  try
    LResponse := LClient.PostEmpty(LPath);
    if (LResponse.StatusCode < 200) or (LResponse.StatusCode >= 300) then
      raise ESearchServiceError.CreateFmt('Scan baslatma basarisiz. HTTP %d', [LResponse.StatusCode]);

    LJsonValue := TJSONObject.ParseJSONValue(LResponse.ContentAsString(TEncoding.UTF8));
    try
      if not (LJsonValue is TJSONObject) then
        raise ESearchServiceError.Create('Scan yaniti gecersiz.');

      LStatusValue := TJSONObject(LJsonValue).GetValue('status');
      LMessageValue := TJSONObject(LJsonValue).GetValue('message');

      if Assigned(LStatusValue) then
        Result.Status := Trim(LStatusValue.Value)
      else
        Result.Status := '';

      if Assigned(LMessageValue) then
        Result.Message := Trim(LMessageValue.Value)
      else
        Result.Message := '';
    finally
      LJsonValue.Free;
    end;
  finally
    LClient.Free;
  end;
end;

end.
