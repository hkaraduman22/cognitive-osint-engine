unit UHistoryService;

interface

uses
  System.SysUtils;

type
  EHistoryServiceError = class(Exception);

  TSearchHistoryItem = record
    Id: Integer;
    Query: string;
    CreatedAt: string;
  end;

  TSearchHistoryItems = TArray<TSearchHistoryItem>;

  THistoryService = class
  public
    function GetHistory(const ABearerToken: string): TSearchHistoryItems;
  end;

implementation

uses
  System.JSON,
  System.Net.HttpClient,
  UHttpApiClient;

function THistoryService.GetHistory(const ABearerToken: string): TSearchHistoryItems;
var
  LClient: THttpApiClient;
  LResponse: IHTTPResponse;
  LJsonValue: TJSONValue;
  LJsonArray: TJSONArray;
  I: Integer;
  LItem: TJSONValue;
  LObj: TJSONObject;
  LRecord: TSearchHistoryItem;

  function GetString(const AObject: TJSONObject; const AName: string): string;
  var
    LValue: TJSONValue;
  begin
    LValue := AObject.GetValue(AName);
    if Assigned(LValue) then
      Result := Trim(LValue.Value)
    else
      Result := '';
  end;

  function GetInt(const AObject: TJSONObject; const AName: string; const ADefault: Integer): Integer;
  var
    LValue: TJSONValue;
  begin
    LValue := AObject.GetValue(AName);
    if not Assigned(LValue) then
      Exit(ADefault);

    if LValue is TJSONNumber then
      Exit(TJSONNumber(LValue).AsInt);

    Result := StrToIntDef(Trim(LValue.Value), ADefault);
  end;
begin
  if Trim(ABearerToken) = '' then
    raise EHistoryServiceError.Create('JWT token bulunamadi.');

  LClient := THttpApiClient.Create;
  try
    LResponse := LClient.Get('/api/v1/search/history', ABearerToken);
    if (LResponse.StatusCode < 200) or (LResponse.StatusCode >= 300) then
      raise EHistoryServiceError.CreateFmt('History basarisiz. HTTP %d', [LResponse.StatusCode]);

    LJsonValue := TJSONObject.ParseJSONValue(LResponse.ContentAsString(TEncoding.UTF8));
    try
      if not (LJsonValue is TJSONArray) then
        raise EHistoryServiceError.Create('History yaniti dizi formatinda degil.');

      LJsonArray := TJSONArray(LJsonValue);
      SetLength(Result, LJsonArray.Count);

      for I := 0 to LJsonArray.Count - 1 do
      begin
        LItem := LJsonArray.Items[I];
        if not (LItem is TJSONObject) then
          raise EHistoryServiceError.Create('History kayit formati gecersiz.');

        LObj := TJSONObject(LItem);
        LRecord.Id := GetInt(LObj, 'id', 0);
        LRecord.Query := GetString(LObj, 'query');
        LRecord.CreatedAt := GetString(LObj, 'created_at');

        Result[I] := LRecord;
      end;
    finally
      LJsonValue.Free;
    end;
  finally
    LClient.Free;
  end;
end;

end.
